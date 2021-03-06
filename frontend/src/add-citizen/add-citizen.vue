

<template>
    <b-modal :visible="showAddModal"
             size="lg"
             hide-header
             hide-footer
             no-close-on-backdrop
             no-close-on-esc
             class="m-0 p-0"
             @shown="setupForm()">
       <div style="display: flex; flex-direction: row; justify-content: space-between" class="modal_header">
         <div><h4>{{modalTitle}}</h4></div>
       </div>
       <b-alert :show="dismissCountDown"
                style="h-align: center"
                variant="danger"
                @dismissed="dismissCountDown=0"
                @dismiss-count-down="countDownChanged">{{this.$store.state.alertMessage}}</b-alert>
      <div v-if="!this.addModalForm.citizen">
        <div class="loader"></div>
      </div>
      <div v-else>
        <AddCitizenForm />
        <b-container class="mt-3 pr-3">
          <b-row align-v="center" align-h="end">
            <div v-if="reception">
              <b-col cols="1" class="p-0 mr-1">Quick Txn?</b-col>
              <b-col col cols="1" class="p-0">
                <b-form-checkbox  v-model="quickTrans" value="1" unchecked-value="0"/>
              </b-col>
            </div>
            <Buttons />
          </b-row>
        </b-container>
      </div>
    </b-modal>
</template>

<script>

import {
  mapState, mapGetters, mapMutations, mapActions
}
from 'vuex'
import Buttons from './form-components/buttons'
import AddCitizenForm from './add-citizen-form'

export default {
    name: 'AddCitizen',

    components: {
        AddCitizenForm, Buttons
    },

    mounted() {
      this.$root.$on('showAddMessage', () => {
        this.showAlert()
      })
    },

    data() {
      return {
        dismissSecs: 5,
        dismissCountDown: 0
      }
    },

    computed: {
      ...mapState(['addCitizenModal', 'addModalForm', 'showAddModal', 'addModalSetup', 'serviceModalForm']),
      ...mapGetters(['form_data', 'reception']),

      modalTitle() {
        if (this.addModalSetup === 'edit_mode') {
          return 'Edit Service'
        } else {
          return 'Add Citizen'
        }
      },

      quickTrans: {
        get() { return this.form_data.quick },
        set(value) { this.updateAddModalForm({type:'quick',value}) }
      }
    },

    methods: {
      ...mapActions(['cancelAddCitizensModal']),
      ...mapMutations(['updateAddModalForm', 'setDefaultChannel']),

      countDownChanged (dismissCountDown) {
        this.dismissCountDown = dismissCountDown
      },
      setupForm() {
        let setup = this.addModalSetup
        if (setup === 'add_mode' || setup === 'edit_mode') {
          this.$root.$emit( 'focusfilter' )
        } else {
          if (!this.reception) {
            this.$root.$emit( 'focusfilter' )
          } else if (this.reception) {
            this.$root.$emit( 'focuscomments' )
          }
        }
      },
      showAlert () {
        this.dismissCountDown = this.dismissSecs
      }
    }
  }
</script>

<style>
  .disabled {
    background-color: #8e9399 !important;
    color: Gainsboro !important;
  }
  .disabled:hover {
    background-color: #8e9399 !important;
  }
  .loader {
    position: relative;
    text-align: center;
    margin: 15px auto 35px auto;
    z-index: 9999;
    display: block;
    width: 80px;
    height: 80px;
    border: 10px solid rgba(0, 0, 0, .3);
    border-radius: 50%;
    border-top-color: #000;
    animation: spin 1s ease-in-out infinite;
    -webkit-animation: spin 1s ease-in-out infinite;
  }
  @keyframes spin {
    to {
      -webkit-transform: rotate(360deg);
    }
  }

  @-webkit-keyframes spin {
    to {
      -webkit-transform: rotate(360deg);
    }
  }
</style>
