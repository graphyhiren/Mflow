import React from 'react';
import { shallow } from 'enzyme';
import { ParallelCoordinatesPlotView } from './ParallelCoordinatesPlotView';

describe('unit tests', () => {
  let wrapper;
  let instance;
  let mininumProps;

  beforeEach(() => {
    mininumProps = {
      runUuids: ['runUuid_0', 'runUuid_1'],
      paramKeys: ['param_0', 'param_1'],
      metricKeys: ['metric_0', 'metric_1'],
      paramDimensions: [
        {
          label: 'param_0',
          values: [1, 2],
        },
        {
          label: 'param_1',
          values: [2, 3],
        },
      ],
      metricDimensions: [
        {
          label: 'metric_0',
          values: [1, 2],
        },
        {
          label: 'metric_1',
          values: [2, 3],
        },
      ],
    };
  });

  test('should render with minimal props without exploding', () => {
    wrapper = shallow(<ParallelCoordinatesPlotView {...mininumProps}/>);
    expect(wrapper.length).toBe(1);
  });

  test('getDerivedStateFromProps should return null when the selections do not change', () => {
    const props = {
      paramKeys: ['param_0', 'param_1'],
      metricKeys: ['metric_0', 'metric_1'],
    };
    // state with different order but same selections
    const state = {
      sequence: ['param_0', 'metric_0', 'metric_1', 'param_1'],
    };
    expect(ParallelCoordinatesPlotView.getDerivedStateFromProps(props, state)).toBe(null);
  });

  test('getDerivedStateFromProps should return state when the selections changes', () => {
    const props = {
      paramKeys: ['param_0', 'param_1'],
      metricKeys: ['metric_0', 'metric_1', 'metric_2'], // props comes with an extra metric_2
    };
    const state = {
      sequence: ['param_0', 'metric_0', 'metric_1', 'param_1'],
    };
    expect(ParallelCoordinatesPlotView.getDerivedStateFromProps(props, state)).toEqual({
      sequence: ['param_0', 'param_1', 'metric_0', 'metric_1', 'metric_2'],
    });
  });
});
