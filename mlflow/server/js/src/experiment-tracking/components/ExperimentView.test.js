import React from 'react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import FileSaver from 'file-saver';
import { BrowserRouter } from 'react-router-dom';

import { ExperimentViewWithIntl, mapStateToProps } from './ExperimentView';
import ExperimentViewUtil from './ExperimentViewUtil';
import Fixtures from '../utils/test-utils/Fixtures';
import {
  addApiToState,
  addExperimentToState,
  addExperimentTagsToState,
  createPendingApi,
  emptyState,
} from '../utils/test-utils/ReduxStoreFixtures';
import Utils from '../../common/utils/Utils';
import { Spinner } from '../../common/components/Spinner';
import { ExperimentViewPersistedState } from '../sdk/MlflowLocalStorageMessages';
import { getUUID } from '../../common/utils/ActionUtils';
import { Metric, Param, RunTag, RunInfo } from '../sdk/MlflowMessages';
import { mountWithIntl, shallowWithInjectIntl } from '../../common/utils/TestUtils';
import {
  COLUMN_TYPES,
  LIFECYCLE_FILTER,
  MODEL_VERSION_FILTER,
  DEFAULT_ORDER_BY_KEY,
  DEFAULT_ORDER_BY_ASC,
  DEFAULT_START_TIME,
  DEFAULT_CATEGORIZED_UNCHECKED_KEYS,
  DEFAULT_SHOW_MULTI_COLUMNS,
  DEFAULT_DIFF_SWITCH_SELECTED,
  COLUMN_SORT_BY_ASC,
  COLUMN_SORT_BY_DESC,
  DEFAULT_LIFECYCLE_FILTER,
  DEFAULT_MODEL_VERSION_FILTER,
} from '../constants';

const EXPERIMENT_ID = '3';

let onSearchSpy;
let historyPushSpy;

beforeEach(() => {
  onSearchSpy = jest.fn();
  historyPushSpy = jest.fn();
});

const getDefaultExperimentViewProps = () => {
  return {
    onSearch: onSearchSpy,
    runInfos: [
      RunInfo.fromJs({
        run_uuid: 'run-id',
        experiment_id: EXPERIMENT_ID,
        status: 'FINISHED',
        start_time: 1,
        end_time: 1,
        artifact_uri: 'dummypath',
        lifecycle_stage: 'active',
      }),
    ],
    experiment: Fixtures.createExperiment(),
    experimentId: EXPERIMENT_ID,
    history: {
      location: {
        pathname: '/',
      },
      push: historyPushSpy,
    },
    paramKeyList: ['batch_size'],
    metricKeyList: ['acc'],
    paramsList: [[Param.fromJs({ key: 'batch_size', value: '512' })]],
    metricsList: [[Metric.fromJs({ key: 'acc', value: 0.1 })]],
    tagsList: [],
    experimentTags: {},
    modelVersionFilter: DEFAULT_MODEL_VERSION_FILTER,
    lifecycleFilter: DEFAULT_LIFECYCLE_FILTER,
    searchInput: '',
    searchRunsError: '',
    isLoading: true,
    loadingMore: false,
    handleLoadMoreRuns: jest.fn(),
    orderByKey: DEFAULT_ORDER_BY_KEY,
    orderByAsc: DEFAULT_ORDER_BY_ASC,
    startTime: DEFAULT_START_TIME,
    setExperimentTagApi: jest.fn(),
    location: { pathname: '/' },
    modelVersionsByRunUuid: {},
  };
};

const getExperimentViewMock = (componentProps = {}) => {
  const mergedProps = { ...getDefaultExperimentViewProps(), ...componentProps };
  return shallowWithInjectIntl(<ExperimentViewWithIntl {...mergedProps} />);
};

const mountExperimentViewMock = (componentProps = {}) => {
  const mergedProps = { ...getDefaultExperimentViewProps(), ...componentProps };
  const store = configureStore()(emptyState);
  return mountWithIntl(
    <Provider store={store}>
      <BrowserRouter>
        <ExperimentViewWithIntl {...mergedProps} />
      </BrowserRouter>
    </Provider>,
  );
};

const createTags = (tags) => {
  // Converts {key: value, ...} to {key: RunTag(key, value), ...}
  return Object.entries(tags).reduce(
    (acc, [key, value]) => ({ ...acc, [key]: RunTag.fromJs({ key, value }) }),
    {},
  );
};

test('Should render with minimal props without exploding', () => {
  const wrapper = getExperimentViewMock();
  expect(wrapper.length).toBe(1);
});

test('Should render compact view without exploding', () => {
  const wrapper = mountExperimentViewMock({ isLoading: false, forceCompactTableView: true });
  expect(wrapper.find('ExperimentRunsTableCompactView').text()).toContain('batch_size:512');
  expect(wrapper.length).toBe(1);
});

test('Loading state without any URL params', () => {
  const wrapper = getExperimentViewMock();
  const { state } = wrapper.instance();
  expect(state.persistedState.showMultiColumns).toEqual(DEFAULT_SHOW_MULTI_COLUMNS);
  expect(state.persistedState.categorizedUncheckedKeys).toEqual(DEFAULT_CATEGORIZED_UNCHECKED_KEYS);
  expect(state.persistedState.diffSwitchSelected).toEqual(DEFAULT_DIFF_SWITCH_SELECTED);
  expect(state.persistedState.preSwitchCategorizedUncheckedKeys).toEqual(
    DEFAULT_CATEGORIZED_UNCHECKED_KEYS,
  );
  expect(state.persistedState.postSwitchCategorizedUncheckedKeys).toEqual(
    DEFAULT_CATEGORIZED_UNCHECKED_KEYS,
  );
});

test('Loading state with all URL params', () => {
  const location = {};
  location.search =
    'startTime=ALL&orderByKey=attributes.start_time' +
    '&showMultiColumns=false' +
    '&diffSwitchSelected=true' +
    '&categorizedUncheckedKeys%5Battributes%5D%5B0%5D=a1' +
    '&categorizedUncheckedKeys%5Bparams%5D%5B0%5D=p1' +
    '&categorizedUncheckedKeys%5Bmetrics%5D%5B0%5D=m1' +
    '&categorizedUncheckedKeys%5Btags%5D%5B0%5D=t1' +
    '&preSwitchCategorizedUncheckedKeys%5Battributes%5D%5B0%5D=a2' +
    '&preSwitchCategorizedUncheckedKeys%5Bparams%5D%5B0%5D=p2' +
    '&preSwitchCategorizedUncheckedKeys%5Bmetrics%5D%5B0%5D=m2' +
    '&preSwitchCategorizedUncheckedKeys%5Btags%5D%5B0%5D=t2' +
    '&postSwitchCategorizedUncheckedKeys%5Battributes%5D%5B0%5D=a3' +
    '&postSwitchCategorizedUncheckedKeys%5Bparams%5D%5B0%5D=p3' +
    '&postSwitchCategorizedUncheckedKeys%5Bmetrics%5D%5B0%5D=m3' +
    '&postSwitchCategorizedUncheckedKeys%5Btags%5D%5B0%5D=t3';
  const wrapper = getExperimentViewMock({ location });
  const { state } = wrapper.instance();
  expect(state.persistedState.showMultiColumns).toEqual(false);
  expect(state.persistedState.diffSwitchSelected).toEqual(true);
  expect(state.persistedState.categorizedUncheckedKeys).toEqual({
    [COLUMN_TYPES.ATTRIBUTES]: ['a1'],
    [COLUMN_TYPES.PARAMS]: ['p1'],
    [COLUMN_TYPES.METRICS]: ['m1'],
    [COLUMN_TYPES.TAGS]: ['t1'],
  });
  expect(state.persistedState.preSwitchCategorizedUncheckedKeys).toEqual({
    [COLUMN_TYPES.ATTRIBUTES]: ['a2'],
    [COLUMN_TYPES.PARAMS]: ['p2'],
    [COLUMN_TYPES.METRICS]: ['m2'],
    [COLUMN_TYPES.TAGS]: ['t2'],
  });
  expect(state.persistedState.postSwitchCategorizedUncheckedKeys).toEqual({
    [COLUMN_TYPES.ATTRIBUTES]: ['a3'],
    [COLUMN_TYPES.PARAMS]: ['p3'],
    [COLUMN_TYPES.METRICS]: ['m3'],
    [COLUMN_TYPES.TAGS]: ['t3'],
  });
});

test(`Clearing filter state calls search handler with correct arguments`, () => {
  const wrapper = getExperimentViewMock();
  wrapper.instance().onClear();
  expect(onSearchSpy.mock.calls.length).toBe(1);
  expect(onSearchSpy.mock.calls[0][0]).toBe('');
  expect(onSearchSpy.mock.calls[0][1]).toBe(DEFAULT_LIFECYCLE_FILTER);
  expect(onSearchSpy.mock.calls[0][2]).toBe(DEFAULT_ORDER_BY_KEY);
  expect(onSearchSpy.mock.calls[0][3]).toBe(DEFAULT_ORDER_BY_ASC);
  expect(onSearchSpy.mock.calls[0][4]).toBe(DEFAULT_MODEL_VERSION_FILTER);
  expect(onSearchSpy.mock.calls[0][5]).toBe(DEFAULT_START_TIME);
});

test('Onboarding alert shows', () => {
  const wrapper = getExperimentViewMock();
  expect(wrapper.find('Alert')).toHaveLength(1);
});

test('Onboarding alert does not show if disabled', () => {
  const wrapper = getExperimentViewMock();
  const instance = wrapper.instance();
  instance.setState({
    showOnboardingHelper: false,
  });
  expect(wrapper.find('Alert')).toHaveLength(0);
});

test('ExperimentView will show spinner if isLoading prop is true', () => {
  const wrapper = getExperimentViewMock();
  const instance = wrapper.instance();
  instance.setState({
    persistedState: new ExperimentViewPersistedState({ showMultiColumns: false }).toJSON(),
  });
  expect(wrapper.find(Spinner)).toHaveLength(1);
});

test('Page title is set', () => {
  const mockUpdatePageTitle = jest.fn();
  Utils.updatePageTitle = mockUpdatePageTitle;
  getExperimentViewMock();
  expect(mockUpdatePageTitle.mock.calls[0][0]).toBe('Default - MLflow Experiment');
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
    metricKeyList: [],
    paramKeyList: [],
    metricsList: [],
    paramsList: [],
    tagsList: [],
    experimentTags: {},
    modelVersionsByRunUuid: {},
  });
});

describe('Download CSV', () => {
  const mlflowSystemTags = {
    'mlflow.runName': 'name',
    'mlflow.source.name': 'src.py',
    'mlflow.source.type': 'LOCAL',
    'mlflow.user': 'user',
  };

  const blobOptionExpected = { type: 'application/csv;charset=utf-8' };
  const filenameExpected = 'runs.csv';
  const startTimeStringExpected = Utils.formatTimestamp(
    getDefaultExperimentViewProps().runInfos[0].start_time,
  );
  const saveAsSpy = jest.spyOn(FileSaver, 'saveAs');
  const blobSpy = jest.spyOn(global, 'Blob').mockImplementation((content, options) => {
    return { content, options };
  });

  afterEach(() => {
    saveAsSpy.mockClear();
    blobSpy.mockClear();
  });

  test('Downloaded CSV contains tags', () => {
    const tagsList = [
      createTags({
        ...mlflowSystemTags,
        a: '0',
        b: '1',
      }),
    ];
    const csvExpected = `
Start Time,Duration,Run ID,Name,Source Type,Source Name,User,Status,batch_size,acc,a,b
${startTimeStringExpected},0ms,run-id,name,LOCAL,src.py,user,FINISHED,512,0.1,0,1
`.substring(1); // strip a leading newline

    const wrapper = getExperimentViewMock({ tagsList });
    wrapper.instance().onDownloadCsv();
    expect(saveAsSpy).toHaveBeenCalledWith(expect.anything(), filenameExpected);
    expect(blobSpy).toHaveBeenCalledWith([csvExpected], blobOptionExpected);
  });

  test('Downloaded CSV does not contain unchecked tags', () => {
    const tagsList = [
      createTags({
        ...mlflowSystemTags,
        a: '0',
        b: '1',
      }),
    ];
    const csvExpected = `
Start Time,Duration,Run ID,Name,Source Type,Source Name,User,Status,batch_size,acc,a
${startTimeStringExpected},0ms,run-id,name,LOCAL,src.py,user,FINISHED,512,0.1,0
`.substring(1);

    const wrapper = getExperimentViewMock({ tagsList });
    // Uncheck the tag 'b'
    wrapper.setState({
      persistedState: {
        categorizedUncheckedKeys: { [COLUMN_TYPES.TAGS]: ['b'], [COLUMN_TYPES.ATTRIBUTES]: [] },
      },
    });
    // Then, download CSV
    wrapper.instance().onDownloadCsv();
    expect(saveAsSpy).toHaveBeenCalledWith(expect.anything(), filenameExpected);
    expect(blobSpy).toHaveBeenCalledWith([csvExpected], blobOptionExpected);
  });

  test('CSV download succeeds without tags', () => {
    const tagsList = [createTags(mlflowSystemTags)];
    const csvExpected = `
Start Time,Duration,Run ID,Name,Source Type,Source Name,User,Status,batch_size,acc
${startTimeStringExpected},0ms,run-id,name,LOCAL,src.py,user,FINISHED,512,0.1
`.substring(1);

    const wrapper = getExperimentViewMock({ tagsList });
    wrapper.instance().onDownloadCsv();
    expect(saveAsSpy).toHaveBeenCalledWith(expect.anything(), filenameExpected);
    expect(blobSpy).toHaveBeenCalledWith([csvExpected], blobOptionExpected);
  });
});

describe('ExperimentView event handlers', () => {
  let wrapper;
  let instance;

  const getSearchParams = ({
    searchInput = '',
    lifecycleFilter = DEFAULT_LIFECYCLE_FILTER,
    modelVersionFilter = DEFAULT_MODEL_VERSION_FILTER,
    orderByKey = DEFAULT_ORDER_BY_KEY,
    orderByAsc = DEFAULT_ORDER_BY_ASC,
    startTime = DEFAULT_START_TIME,
  } = {}) => [searchInput, lifecycleFilter, orderByKey, orderByAsc, modelVersionFilter, startTime];

  beforeEach(() => {
    wrapper = getExperimentViewMock({});
    instance = wrapper.instance();
    Object.assign(navigator, {
      clipboard: {
        writeText: () => {},
      },
    });
  });

  test('handleLifecycleFilterInput calls onSearch with the right params', () => {
    const newFilterInput = LIFECYCLE_FILTER.DELETED;
    instance.handleLifecycleFilterInput({ key: newFilterInput });

    expect(onSearchSpy).toHaveBeenCalledTimes(1);
    expect(onSearchSpy).toBeCalledWith(
      ...getSearchParams({
        lifecycleFilter: newFilterInput,
      }),
    );
  });

  test('handleModelVersionFilterInput calls onSearch with the right params', () => {
    const newFilterInput = MODEL_VERSION_FILTER.WTIHOUT_MODEL_VERSIONS;
    instance.handleModelVersionFilterInput({ key: newFilterInput });

    expect(onSearchSpy).toHaveBeenCalledTimes(1);
    expect(onSearchSpy).toBeCalledWith(
      ...getSearchParams({
        modelVersionFilter: newFilterInput,
      }),
    );
  });

  test('onShare copies default state to clipboard', () => {
    const updateUrlWithViewStateSpy = jest.spyOn(instance, 'updateUrlWithViewState');
    const writeTextSpy = jest.spyOn(navigator.clipboard, 'writeText');

    // Set default state
    instance.state.persistedState = new ExperimentViewPersistedState().toJSON();

    instance.onShare();

    const expectedHistoryPush =
      `/experiments/${EXPERIMENT_ID}/s?startTime=ALL` +
      `&orderByKey=attributes.start_time&lifecycle=Active&modelVersion=All%20Runs`;
    expect(updateUrlWithViewStateSpy).toHaveBeenCalledTimes(1);
    expect(historyPushSpy).toHaveBeenCalledWith(expectedHistoryPush);
    expect(writeTextSpy).toHaveBeenCalledTimes(1);
  });

  test('onShare copies edited state & props to clipboard', () => {
    wrapper = getExperimentViewMock({
      orderByKey: 'test-key',
    });
    instance = wrapper.instance();

    const updateUrlWithViewStateSpy = jest.spyOn(instance, 'updateUrlWithViewState');
    const writeTextSpy = jest.spyOn(navigator.clipboard, 'writeText');

    // Set non-default state
    instance.state.persistedState = new ExperimentViewPersistedState({
      showMultiColumns: false,
    }).toJSON();

    instance.onShare();

    const expectedHistoryPush =
      `/experiments/${EXPERIMENT_ID}/s?startTime=ALL` +
      '&orderByKey=test-key&lifecycle=Active&modelVersion=All%20Runs&showMultiColumns=false';
    expect(updateUrlWithViewStateSpy).toHaveBeenCalledTimes(1);
    expect(historyPushSpy).toHaveBeenCalledWith(expectedHistoryPush);
    expect(writeTextSpy).toHaveBeenCalledTimes(1);
  });

  test('onClear clears all parameters', () => {
    wrapper = getExperimentViewMock({
      lifecycleFilter: LIFECYCLE_FILTER.DELETED,
      modelVersionFilter: MODEL_VERSION_FILTER.WITH_MODEL_VERSIONS,
      searchInput: 'previous-testing',
    });
    instance = wrapper.instance();
    const testingString = 'testing';
    instance.setState({ searchInput: testingString });

    expect(wrapper.state('searchInput')).toEqual(testingString);

    instance.onClear();
    expect(onSearchSpy).toHaveBeenCalledTimes(1);
    expect(onSearchSpy).toBeCalledWith(
      ...getSearchParams({
        searchInput: '',
        lifecycleFilter: DEFAULT_LIFECYCLE_FILTER,
        orderByKey: DEFAULT_ORDER_BY_KEY,
        orderByAsc: DEFAULT_ORDER_BY_ASC,
        modelVersionFilter: DEFAULT_MODEL_VERSION_FILTER,
        startTime: DEFAULT_START_TIME,
      }),
    );
  });

  test('search filters are correctly applied', () => {
    instance.onSearchInput({
      target: {
        value: 'SearchString',
      },
    });

    instance.onSortBy('orderByKey', true);

    expect(onSearchSpy).toHaveBeenCalledTimes(1);
    expect(onSearchSpy).toBeCalledWith(
      ...getSearchParams({
        orderByKey: 'orderByKey',
        orderByAsc: true,
      }),
    );

    instance.onSearch(undefined, 'SearchString');

    expect(onSearchSpy).toHaveBeenCalledTimes(2);
    expect(onSearchSpy).toBeCalledWith(
      ...getSearchParams({
        orderByKey: 'orderByKey',
        orderByAsc: true,
        mySearchInput: 'SearchString',
      }),
    );
  });
});

describe('Sort by dropdown', () => {
  test('Selecting a sort option sorts the experiment runs correctly', () => {
    const wrapper = mountExperimentViewMock({
      isLoading: false,
      forceCompactTableView: true,
      startTime: 'ALL',
    });

    const sortSelect = wrapper.find("Select [data-test-id='sort-select-dropdown']").first();
    sortSelect.simulate('click');

    expect(wrapper.exists(`[data-test-id="sort-select-User-${COLUMN_SORT_BY_ASC}"] li`)).toBe(true);
    expect(wrapper.exists(`[data-test-id="sort-select-batch_size-${COLUMN_SORT_BY_ASC}"] li`)).toBe(
      true,
    );
    expect(wrapper.exists(`[data-test-id="sort-select-acc-${COLUMN_SORT_BY_ASC}"] li`)).toBe(true);
    expect(wrapper.exists(`[data-test-id="sort-select-User-${COLUMN_SORT_BY_DESC}"] li`)).toBe(
      true,
    );
    expect(
      wrapper.exists(`[data-test-id="sort-select-batch_size-${COLUMN_SORT_BY_DESC}"] li`),
    ).toBe(true);
    expect(wrapper.exists(`[data-test-id="sort-select-acc-${COLUMN_SORT_BY_DESC}"] li`)).toBe(true);

    sortSelect.prop('onChange')('attributes.start_time');
    expect(onSearchSpy).toBeCalledWith(
      '',
      LIFECYCLE_FILTER.ACTIVE,
      'attributes.start_time',
      DEFAULT_ORDER_BY_ASC,
      MODEL_VERSION_FILTER.ALL_RUNS,
      DEFAULT_START_TIME,
    );
  });
});

describe('Start time dropdown', () => {
  test('Selecting a start time option calls the search correctly', () => {
    const wrapper = mountExperimentViewMock({
      isLoading: false,
      forceCompactTableView: true,
      startTime: 'ALL',
    });

    const startTimeSelect = wrapper
      .find("Select [data-test-id='start-time-select-dropdown']")
      .first();
    startTimeSelect.simulate('click');

    expect(wrapper.exists('[data-test-id="start-time-select-ALL"] li')).toBe(true);
    expect(wrapper.exists('[data-test-id="start-time-select-LAST_HOUR"] li')).toBe(true);
    expect(wrapper.exists('[data-test-id="start-time-select-LAST_24_HOURS"] li')).toBe(true);
    expect(wrapper.exists('[data-test-id="start-time-select-LAST_7_DAYS"] li')).toBe(true);
    expect(wrapper.exists('[data-test-id="start-time-select-LAST_30_DAYS"] li')).toBe(true);
    expect(wrapper.exists('[data-test-id="start-time-select-LAST_YEAR"] li')).toBe(true);

    startTimeSelect.prop('onChange')('LAST_7_DAYS');
    expect(onSearchSpy).toBeCalledWith(
      '',
      LIFECYCLE_FILTER.ACTIVE,
      DEFAULT_ORDER_BY_KEY,
      DEFAULT_ORDER_BY_ASC,
      MODEL_VERSION_FILTER.ALL_RUNS,
      'LAST_7_DAYS',
    );
  });
});

describe('handleDiffSwitchChange', () => {
  let getCategorizedUncheckedKeysDiffViewSpy;
  let instance;
  let wrapper;

  beforeEach(() => {
    getCategorizedUncheckedKeysDiffViewSpy = jest
      .spyOn(ExperimentViewUtil, 'getCategorizedUncheckedKeysDiffView')
      .mockImplementation(() => {
        return {
          [COLUMN_TYPES.ATTRIBUTES]: ['a1'],
          [COLUMN_TYPES.PARAMS]: ['p1'],
          [COLUMN_TYPES.METRICS]: ['m1'],
          [COLUMN_TYPES.TAGS]: ['t1'],
        };
      });
    wrapper = getExperimentViewMock();
    instance = wrapper.instance();
    instance.getCategorizedUncheckedKeysDiffView = getCategorizedUncheckedKeysDiffViewSpy;
  });

  test('handleDiffSwitchChange changes state correctly', () => {
    const handleColumnSelectionCheckSpy = jest.fn();
    instance.handleColumnSelectionCheck = handleColumnSelectionCheckSpy;

    // Switch turned off by default
    expect(wrapper.state().persistedState.diffSwitchSelected).toBe(false);

    // Switch turned on
    instance.handleDiffSwitchChange();
    expect(wrapper.state().persistedState.diffSwitchSelected).toBe(true);
    expect(getCategorizedUncheckedKeysDiffViewSpy).toHaveBeenCalledTimes(1);
    expect(handleColumnSelectionCheckSpy).toHaveBeenCalledTimes(1);
    expect(handleColumnSelectionCheckSpy).toHaveBeenLastCalledWith({
      [COLUMN_TYPES.ATTRIBUTES]: ['a1'],
      [COLUMN_TYPES.PARAMS]: ['p1'],
      [COLUMN_TYPES.METRICS]: ['m1'],
      [COLUMN_TYPES.TAGS]: ['t1'],
    });

    // Switch turned off
    instance.handleDiffSwitchChange();
    expect(wrapper.state().persistedState.diffSwitchSelected).toBe(false);
    expect(getCategorizedUncheckedKeysDiffViewSpy).toHaveBeenCalledTimes(1);
    expect(handleColumnSelectionCheckSpy).toHaveBeenCalledTimes(2);
    expect(handleColumnSelectionCheckSpy).toHaveBeenLastCalledWith(
      DEFAULT_CATEGORIZED_UNCHECKED_KEYS,
    );
  });

  test('handleDiffSwitchChange maintains state of pre-switch unchecked columns', () => {
    expect(wrapper.state().persistedState.diffSwitchSelected).toBe(false);
    instance.handleColumnSelectionCheck({
      [COLUMN_TYPES.ATTRIBUTES]: ['a2'],
      [COLUMN_TYPES.PARAMS]: ['p2'],
      [COLUMN_TYPES.METRICS]: ['m2'],
      [COLUMN_TYPES.TAGS]: ['t2'],
    });

    // Switch turned on
    instance.handleDiffSwitchChange();
    expect(wrapper.state().persistedState.preSwitchCategorizedUncheckedKeys).toEqual({
      [COLUMN_TYPES.ATTRIBUTES]: ['a2'],
      [COLUMN_TYPES.PARAMS]: ['p2'],
      [COLUMN_TYPES.METRICS]: ['m2'],
      [COLUMN_TYPES.TAGS]: ['t2'],
    });
    expect(wrapper.state().persistedState.postSwitchCategorizedUncheckedKeys).toEqual({
      [COLUMN_TYPES.ATTRIBUTES]: ['a1'],
      [COLUMN_TYPES.PARAMS]: ['p1'],
      [COLUMN_TYPES.METRICS]: ['m1'],
      [COLUMN_TYPES.TAGS]: ['t1'],
    });
    expect(wrapper.state().persistedState.categorizedUncheckedKeys).toEqual({
      [COLUMN_TYPES.ATTRIBUTES]: ['a1'],
      [COLUMN_TYPES.PARAMS]: ['p1'],
      [COLUMN_TYPES.METRICS]: ['m1'],
      [COLUMN_TYPES.TAGS]: ['t1'],
    });

    // Switch turned off
    instance.handleDiffSwitchChange();
    expect(wrapper.state().persistedState.categorizedUncheckedKeys).toEqual({
      [COLUMN_TYPES.ATTRIBUTES]: ['a2'],
      [COLUMN_TYPES.PARAMS]: ['p2'],
      [COLUMN_TYPES.METRICS]: ['m2'],
      [COLUMN_TYPES.TAGS]: ['t2'],
    });
  });

  test('handleDiffSwitchChange maintains state of unchecked columns while in switch state', () => {
    // Columns unchecked before turning switch on
    instance.handleColumnSelectionCheck({
      [COLUMN_TYPES.ATTRIBUTES]: ['a2'],
      [COLUMN_TYPES.PARAMS]: ['p2'],
      [COLUMN_TYPES.METRICS]: ['m2'],
      [COLUMN_TYPES.TAGS]: ['t2'],
    });

    // Switch turned on
    instance.handleDiffSwitchChange();

    // Change unchecked columns
    instance.handleColumnSelectionCheck({
      [COLUMN_TYPES.ATTRIBUTES]: ['a1', 'a3'], // select a3
      [COLUMN_TYPES.PARAMS]: [], // deselect p1
      [COLUMN_TYPES.METRICS]: ['m1', 'm3'],
      [COLUMN_TYPES.TAGS]: [],
    });

    // Switch turned off
    instance.handleDiffSwitchChange();

    // Expect previous state, plus changes during switch state
    expect(wrapper.state().persistedState.categorizedUncheckedKeys).toEqual({
      [COLUMN_TYPES.ATTRIBUTES]: ['a2', 'a3'],
      [COLUMN_TYPES.PARAMS]: ['p2'],
      [COLUMN_TYPES.METRICS]: ['m2', 'm3'],
      [COLUMN_TYPES.TAGS]: ['t2'],
    });
  });
});
