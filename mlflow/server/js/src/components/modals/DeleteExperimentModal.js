import React, { Component } from 'react';
import { ConfirmModal } from './ConfirmModal';
import PropTypes from 'prop-types';
import { deleteExperimentApi, listExperimentsApi, getUUID } from '../../Actions';
import Routes from '../../Routes';
import Utils from '../../utils/Utils';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

class DeleteExperimentModal extends Component {
  static propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    activeExperimentId: PropTypes.number,
    experimentId: PropTypes.number.isRequired,
    experimentName: PropTypes.string.isRequired,
    deleteExperimentApi: PropTypes.func.isRequired,
    listExperimentsApi: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
  };

  handleSubmit = () => {
    const {experimentId, activeExperimentId} = this.props;
    const deleteExperimentRequestId = getUUID();

    const deletePromise = this.props.deleteExperimentApi(experimentId, deleteExperimentRequestId)
      .then(() => {
        // check whether the deleted experiment is currently selected
        if (experimentId === activeExperimentId) {
          // navigate to root URL and let route pick the next active experiment to show
          this.props.history.push(Routes.rootRoute);
        }
      })
      .then(() => this.props.listExperimentsApi(deleteExperimentRequestId))
      .catch((e) => {
        Utils.logErrorAndNotifyUser(e);
      });

    return deletePromise;
  }

  render() {
    return (
      <ConfirmModal
        isOpen={this.props.isOpen}
        onClose={this.props.onClose}
        handleSubmit={this.handleSubmit}
        title={`Delete Experiment "${this.props.experimentName}"`}
        helpText={
          <div>
            <p>
              <b>
                Experiment "{this.props.experimentName}"
                (Experiment ID: {this.props.experimentId}) will be deleted.
              </b>
            </p>
            {
              process.env.SHOW_GDPR_PURGING_MESSAGES === 'true' ?
              <p>
                Deleted experiments are restorable for 30 days, after which they are purged.
                <br />
                Artifacts are not automatically purged and must be manually deleted.
              </p> : ""
            }
          </div>
        }
        confirmButtonText={"Delete"}
      />
    );
  }
}

const mapDispatchToProps = {
  deleteExperimentApi,
  listExperimentsApi,
};

export default withRouter(connect(undefined, mapDispatchToProps)(DeleteExperimentModal));
