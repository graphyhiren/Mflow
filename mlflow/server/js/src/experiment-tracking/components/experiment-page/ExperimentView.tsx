import { Skeleton } from '@databricks/design-system';
import { useEffect } from 'react';
import { ErrorCodes } from '../../../common/constants';
import NotFoundPage from '../NotFoundPage';
import { PermissionDeniedView } from '../PermissionDeniedView';
import { ExperimentViewDescriptions } from './components/ExperimentViewDescriptions';
import { ExperimentViewNotes } from './components/ExperimentViewNotes';
import { ExperimentViewOnboarding } from './components/ExperimentViewOnboarding';
import { ExperimentViewHeader } from './components/header/ExperimentViewHeader';
import { ExperimentViewHeaderCompare } from './components/header/ExperimentViewHeaderCompare';
import { ExperimentViewRuns } from './components/runs/ExperimentViewRuns';
import { useExperimentIdsNotInState } from './hooks/useExperimentIdsNotInState';
import { useExperimentIds } from './hooks/useExperimentIds';
import { useExperiments } from './hooks/useExperiments';
import { useFetchExperiments } from './hooks/useFetchExperiments';

export const ExperimentView = () => {
  const experimentIds = useExperimentIds();

  const { fetchExperiments, isLoadingExperiment, requestError } = useFetchExperiments();
  const experiments = useExperiments(experimentIds);
  // Need to fetch ids that aren't local if state is cleared
  const idsNotInState = useExperimentIdsNotInState(experimentIds);
  const [firstExperiment] = experiments;

  useEffect(() => {
    fetchExperiments(idsNotInState);
  }, [fetchExperiments, experimentIds, idsNotInState]);

  const isComparingExperiments = experimentIds.length > 1;

  if (requestError && requestError.getErrorCode() === ErrorCodes.PERMISSION_DENIED) {
    return <PermissionDeniedView errorMessage={requestError.getMessageField()} />;
  }

  if (requestError && requestError.getErrorCode() === ErrorCodes.RESOURCE_DOES_NOT_EXIST) {
    return <NotFoundPage />;
  }

  if (isLoadingExperiment || !firstExperiment) {
    return <Skeleton active />;
  }

  return (
    <>
      {isComparingExperiments ? (
        <ExperimentViewHeaderCompare experiments={experiments} />
      ) : (
        <>
          <ExperimentViewHeader experiment={firstExperiment} />
          <ExperimentViewOnboarding />
          <ExperimentViewDescriptions experiment={firstExperiment} />
          <ExperimentViewNotes experiment={firstExperiment} />
        </>
      )}

      <ExperimentViewRuns experiments={experiments} />
    </>
  );
};

export default ExperimentView;
