'''Copyright 2018 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''

from flask import request, g
from flask_restplus import Resource
from qsystem import api, api_call_with_retry, db, oidc, socketio
from app.models import Citizen, CSR, CitizenState
from app.schemas import CitizenSchema, ServiceReqSchema
from app.models import SRState
from datetime import datetime
from ...snowplow.snowplow import SnowPlow

@api.route("/citizens/<int:id>/citizen_left/", methods=['POST'])
class CitizenLeft(Resource):

    service_request_schema = ServiceReqSchema(many=True)
    citizen_schema = CitizenSchema()

    @oidc.accept_token(require_token=True)
    @api_call_with_retry
    def post(self, id):

        csr = CSR.query.filter_by(username=g.oidc_token_info['username'].split("idir/")[-1]).first()
        citizen = Citizen.query.filter_by(citizen_id=id, office_id=csr.office_id).first()
        sr_state = SRState.query.filter_by(sr_code="Complete").first()

        #  Save this service for the Snowplow call later.
        active_service_request = citizen.get_active_service_request()

        for service_request in citizen.service_reqs:

            service_request.sr_state_id = sr_state.sr_state_id

            for p in service_request.periods:
                if p.time_end is None:
                    p.time_end = datetime.now()

        citizen.cs = CitizenState.query.filter_by(cs_state_name='Left before receiving services').first()
        citizen.citizen_comments = None

        db.session.add(citizen)
        db.session.commit()

        SnowPlow.snowplow_event(citizen.citizen_id, csr, "customerleft")

        socketio.emit('update_customer_list', {}, room=csr.office_id)
        socketio.emit('citizen_invited', {}, room='sb-%s' % csr.office.office_number)
        result = self.citizen_schema.dump(citizen)
        socketio.emit('update_active_citizen', result.data, room=csr.office_id)

        return {'citizen': result.data,
                'errors': result.errors}, 200
