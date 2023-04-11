import React from 'react';
import _ from 'lodash';
import { Modal, Button } from '@databricks/design-system';
import { FormattedMessage, injectIntl } from 'react-intl';
import { withMFEAttributes } from '../../mfe/MFEAttributesContext';

import {
  RegisterModelForm,
  CREATE_NEW_MODEL_OPTION_VALUE,
  SELECTED_MODEL_FIELD,
  MODEL_NAME_FIELD,
} from './RegisterModelForm';
import {
  createRegisteredModelApi,
  createModelVersionApi,
  searchModelVersionsApi,
  searchRegisteredModelsApi,
} from '../actions';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import Utils from '../../common/utils/Utils';
import { getUUID } from '../../common/utils/ActionUtils';
import { getModelNameFilter } from '../../model-registry/utils/SearchUtils';

const MAX_SEARCH_REGISTERED_MODELS = 5; // used in drop-down list so not many are visible at once

export class RegisterModelButtonImpl extends React.Component {
  static propTypes = {
    // own props
    disabled: PropTypes.bool.isRequired,
    runUuid: PropTypes.string.isRequired,
    modelPath: PropTypes.string,
    // connected props
    modelByName: PropTypes.object.isRequired,
    appAttributes: PropTypes.object,
    runInfo: PropTypes.object,
    createRegisteredModelApi: PropTypes.func.isRequired,
    createModelVersionApi: PropTypes.func.isRequired,
    searchModelVersionsApi: PropTypes.func.isRequired,
    searchRegisteredModelsApi: PropTypes.func.isRequired,
    intl: PropTypes.shape({ formatMessage: PropTypes.func.isRequired }).isRequired,
  };

  state = {
    visible: false,
    confirmLoading: false,
    modelByName: {},
  };

  createRegisteredModelRequestId = getUUID();

  createModelVersionRequestId = getUUID();

  searchModelVersionRequestId = getUUID();

  constructor() {
    super();
    this.form = React.createRef();
  }

  showRegisterModal = () => {
    // Check if there is a custom action defined for model registration
    const { registerModel } = this.props.appAttributes?.customActionCallbacks || {};
    if (registerModel) {
      // If present, call the custom action listener and return
      registerModel(this.props.runInfo);
      return;
    }

    // If there is no custom action, display regular modal
    this.setState({ visible: true });
  };

  hideRegisterModal = () => {
    this.setState({ visible: false });
  };

  resetAndClearModalForm = () => {
    this.setState({ visible: false, confirmLoading: false });
    this.form.current.resetFields();
  };

  handleRegistrationFailure = (e) => {
    this.setState({ confirmLoading: false });
    Utils.logErrorAndNotifyUser(e);
  };

  handleSearchRegisteredModels = (input) => {
    this.props.searchRegisteredModelsApi(getModelNameFilter(input), MAX_SEARCH_REGISTERED_MODELS);
  };

  reloadModelVersionsForCurrentRun = () => {
    const { runUuid } = this.props;
    return this.props.searchModelVersionsApi({ run_id: runUuid }, this.searchModelVersionRequestId);
  };

  handleRegisterModel = () => {
    this.form.current.validateFields().then((values) => {
      this.setState({ confirmLoading: true });
      const { runUuid, modelPath } = this.props;
      const selectedModelName = values[SELECTED_MODEL_FIELD];
      if (selectedModelName === CREATE_NEW_MODEL_OPTION_VALUE) {
        // When user choose to create a new registered model during the registration, we need to
        // 1. Create a new registered model
        // 2. Create model version #1 in the new registered model
        this.props
          .createRegisteredModelApi(values[MODEL_NAME_FIELD], this.createRegisteredModelRequestId)
          .then(() =>
            this.props.createModelVersionApi(
              values[MODEL_NAME_FIELD],
              modelPath,
              runUuid,
              this.createModelVersionRequestId,
            ),
          )
          .then(this.resetAndClearModalForm)
          .catch(this.handleRegistrationFailure)
          .then(this.reloadModelVersionsForCurrentRun)
          .catch(Utils.logErrorAndNotifyUser);
      } else {
        this.props
          .createModelVersionApi(
            selectedModelName,
            modelPath,
            runUuid,
            this.createModelVersionRequestId,
          )
          .then(this.resetAndClearModalForm)
          .catch(this.handleRegistrationFailure)
          .then(this.reloadModelVersionsForCurrentRun)
          .catch(Utils.logErrorAndNotifyUser);
      }
    });
  };

  componentDidMount() {
    this.props.searchRegisteredModelsApi();
  }

  componentDidUpdate(prevProps, prevState) {
    // Repopulate registered model list every time user launch the modal
    if (prevState.visible === false && this.state.visible === true) {
      this.props.searchRegisteredModelsApi();
    }
  }

  render() {
    const { visible, confirmLoading } = this.state;
    const { disabled, modelByName } = this.props;
    return (
      <div className='register-model-btn-wrapper'>
        <Button
          className='register-model-btn'
          type='primary'
          onClick={this.showRegisterModal}
          disabled={disabled}
          htmlType='button'
        >
          <FormattedMessage
            defaultMessage='Register Model'
            description='Button text to register the model for deployment'
          />
        </Button>
        <Modal
          title={this.props.intl.formatMessage({
            defaultMessage: 'Register Model',
            description: 'Register model modal title to register the model for deployment',
          })}
          width={540}
          visible={visible}
          onOk={this.handleRegisterModel}
          okText={this.props.intl.formatMessage({
            defaultMessage: 'Register',
            description: 'Confirmation text to register the model',
          })}
          confirmLoading={confirmLoading}
          onCancel={this.hideRegisterModal}
          centered
          footer={[
            <Button key='back' onClick={this.hideRegisterModal}>
              <FormattedMessage
                defaultMessage='Cancel'
                description='Cancel button text to cancel the flow to register the model'
              />
            </Button>,
            <Button
              key='submit'
              type='primary'
              onClick={this.handleRegisterModel}
              data-test-id='confirm-register-model'
            >
              <FormattedMessage
                defaultMessage='Register'
                description='Register button text to register the model'
              />
            </Button>,
          ]}
        >
          <RegisterModelForm
            modelByName={modelByName}
            innerRef={this.form}
            onSearchRegisteredModels={_.debounce(this.handleSearchRegisteredModels, 300)}
          />
        </Modal>
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  modelByName: state.entities.modelByName,
  runInfo: state.entities.runInfosByUuid[ownProps.runUuid],
});

const mapDispatchToProps = {
  createRegisteredModelApi,
  createModelVersionApi,
  searchModelVersionsApi,
  searchRegisteredModelsApi,
};

export const RegisterModelButtonWithIntl = injectIntl(RegisterModelButtonImpl);
export const RegisterModelButton = withMFEAttributes(
  connect(mapStateToProps, mapDispatchToProps)(RegisterModelButtonWithIntl),
);
