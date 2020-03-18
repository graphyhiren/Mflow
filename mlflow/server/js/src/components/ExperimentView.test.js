import React from 'react';
import { shallow } from 'enzyme';
import { ExperimentView, mapStateToProps } from './ExperimentView';
import Fixtures from "../test-utils/Fixtures";
import { LIFECYCLE_FILTER } from "./ExperimentPage";
import KeyFilter from "../utils/KeyFilter";
import {
  addApiToState,
  addExperimentToState,
  addExperimentTagsToState,
  addRunToState,
  createPendingApi,
  emptyState,
} from "../test-utils/ReduxStoreFixtures";
import { getUUID } from "../Actions";
import { Spinner } from "./Spinner";
import { ExperimentViewPersistedState } from '../sdk/MlflowLocalStorageMessages';
import { RunInfo } from '../sdk/MlflowMessages';

let onSearchSpy;

beforeEach(() => {
  onSearchSpy = jest.fn();
});

const getExperimentViewMock = () => {
  return shallow(<ExperimentView
    onSearch={onSearchSpy}
    runInfos={[]}
    experiment={Fixtures.createExperiment()}
    history={[]}
    paramKeyList={[]}
    metricKeyList={[]}
    paramsList={[]}
    metricsList={[]}
    tagsList={[]}
    experimentTags={{}}
    paramKeyFilter={new KeyFilter("")}
    metricKeyFilter={new KeyFilter("")}
    lifecycleFilter={LIFECYCLE_FILTER.ACTIVE}
    searchInput={""}
    searchRunsError={''}
    isLoading
    loadingMore={false}
    handleLoadMoreRuns={jest.fn()}
    orderByKey={null}
    orderByAsc={false}
    setExperimentTagApi={jest.fn()}
    location={{ pathname: "/" }}
    tagKeyList={[]}
  />);
};

test(`Clearing filter state calls search handler with correct arguments`, () => {
  const wrapper = getExperimentViewMock();
  wrapper.instance().onClear();
  expect(onSearchSpy.mock.calls.length).toBe(1);
  expect(onSearchSpy.mock.calls[0][0]).toBe('');
  expect(onSearchSpy.mock.calls[0][1]).toBe('');
  expect(onSearchSpy.mock.calls[0][2]).toBe('');
  expect(onSearchSpy.mock.calls[0][3]).toBe(LIFECYCLE_FILTER.ACTIVE);
  expect(onSearchSpy.mock.calls[0][4]).toBe(null);
  expect(onSearchSpy.mock.calls[0][5]).toBe(true);
});

test('Entering search input updates component state', () => {
  const wrapper = getExperimentViewMock();
  wrapper.instance().setState = jest.fn();
  // Test entering search input
  wrapper.find('.ExperimentView-search-input input').first().simulate(
    'change', { target: { value: 'search input string' } });
  expect(wrapper.instance().setState).toBeCalledWith({ searchInput: 'search input string' });
});

test("ExperimentView will show spinner if isLoading prop is true", () => {
  const wrapper = getExperimentViewMock();
  const instance = wrapper.instance();
  instance.setState({
    persistedState: new ExperimentViewPersistedState({ showMultiColumns: false }).toJSON(),
  });
  expect(wrapper.find(Spinner)).toHaveLength(1);
});

// mapStateToProps should only be run after the call to getExperiment from ExperimentPage is
// resolved
test("mapStateToProps doesn't blow up if the searchRunsApi is pending", () => {
  const searchRunsId = getUUID();
  let state = emptyState;
  const experiment = Fixtures.createExperiment();
  state = addApiToState(state, createPendingApi(searchRunsId));
  state = addExperimentToState(state, experiment);
  state = addExperimentTagsToState(state, experiment.experiment_id, []);
  const newProps = mapStateToProps(state, {
    lifecycleFilter: LIFECYCLE_FILTER.ACTIVE,
    searchRunsRequestId: searchRunsId,
    experimentId: experiment.experiment_id,
  });
  expect(newProps).toEqual({
    runInfos: [],
    experiment,
    metricKeyList: [],
    paramKeyList: [],
    metricsList: [],
    paramsList: [],
    tagKeyList: [],
    tagsList: [],
    experimentTags: {},
  });
});

test("params, metrics and tags computation in mapStateToProps", () => {
  const searchRunsId = getUUID();
  let state = emptyState;
  const experiment = Fixtures.createExperiment();
  const run_info = {
    run_uuid: "0",
    experiment_id: experiment.experiment_id.toString(),
    lifecycle_stage: "active",
  };
  const run_data = {
    metrics: [
      {
        key: "metric0",
        step: 0,
        value: 0.0,
        timestamp: 0,
      },
      {
        key: "metric1",
        step: 0,
        value: 1.0,
        timestamp: 0,
      },
    ],
    params: [
      {
        key: "param0",
        value: "val0",
      },
    ],
    tags: [
      {
        key: "tag0",
        value: "val1",
      },
    ],
  };

  state = addRunToState(state, run_info, run_data);
  state = addExperimentToState(state, experiment);
  state = addExperimentTagsToState(state, experiment.experiment_id, []);
  const newProps = mapStateToProps(state, {
    lifecycleFilter: LIFECYCLE_FILTER.ACTIVE,
    searchRunsRequestId: searchRunsId,
    experimentId: experiment.experiment_id,
    metricKeyList: ['metric2'],
    paramKeyList: ['param1'],
    tagKeysList: ['tag1'],
  });
  expect(newProps.runInfos).toEqual([RunInfo.fromJs(run_info)]);
  expect(newProps.metricKeyList).toEqual(['metric0', 'metric1', 'metric2']);
  expect(newProps.paramKeyList).toEqual(['param0', 'param1']);
  expect(newProps.tagKeyList).toEqual(['tag0', 'tag1']);
});
