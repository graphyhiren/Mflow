import React from 'react';
import { shallow } from 'enzyme';
import { MetricsPlotView } from './MetricsPlotView';
import { X_AXIS_RELATIVE, X_AXIS_WALL } from "./MetricsPlotControls";
import { CHART_TYPE_BAR, CHART_TYPE_LINE } from './MetricsPlotPanel';

const metricsForLine = [{
  metricKey: 'metric_0',
  history: [
    {
      key: 'metric_0',
      value: 100,
      step: 0,
      timestamp: 1556662043000,
    },
    {
      key: 'metric_0',
      value: 200,
      step: 1,
      timestamp: 1556662044000,
    },
  ],
  runUuid: 'runUuid1',
  runDisplayName: 'RunDisplayName1',
}, {
  metricKey: 'metric_1',
  history: [
    {
      key: 'metric_1',
      value: 300,
      step: 0,
      timestamp: 1556662043000,
    },
    {
      key: 'metric_0',
      value: 400,
      step: 1,
      timestamp: 1556662044000,
    },
  ],
  runUuid: 'runUuid2',
  runDisplayName: 'RunDisplayName2',
}];

const metricsForBar = [{
  metricKey: 'metric_0',
  history: [
    {
      key: 'metric_0',
      value: 100,
      step: 0,
      timestamp: 1556662043000,
    }
  ],
  runUuid: 'runUuid1',
  runDisplayName: 'RunDisplayName1',
}, {
  metricKey: 'metric_0',
  history: [
    {
      key: 'metric_0',
      value: 300,
      step: 0,
      timestamp: 1556662043000,
    }
  ],
  runUuid: 'runUuid2',
  runDisplayName: 'RunDisplayName2',
}];

describe('test rendering', () => {
  let wrapper;
  let instance;
  let minimalPropsForLineChart;
  let minimalPropsForBarChart;

  beforeEach(() => {
    minimalPropsForLineChart = {
      runUuids: ['runUuid1', 'runUuid2'],
      runDisplayNames: ['RunDisplayName1', 'RunDisplayName2'],
      xAxis: X_AXIS_RELATIVE,
      metrics: metricsForLine,
      metricKeys: ['metric_0', 'metric_1'],
      showPoint: false,
      chartType: CHART_TYPE_LINE,
      isComparing: false,
      yAxisLogScale: false,
      lineSmoothness: 0,
    };
    minimalPropsForBarChart = {
      ...minimalPropsForLineChart,
      metrics: metricsForBar,
      metricKeys: ['metric_0'],
      chartType: CHART_TYPE_BAR,
    };
  });


  test('should render with minimal props without exploding', () => {
    wrapper = shallow(
      <MetricsPlotView {...minimalPropsForLineChart}/>
    );
    expect(wrapper.length).toBe(1);
  });

  test('getPlotPropsForLineChart()', () => {
    wrapper = shallow(<MetricsPlotView {...minimalPropsForLineChart}/>);
    instance = wrapper.instance();
    expect(instance.getPlotPropsForLineChart()).toEqual({
      data: [
        {
          name: 'metric_0',
          x: [0, 1],
          y: [100, 200],
          type: 'scatter',
          mode: 'lines',
          line: {
            shape: 'spline',
            smoothing: 0,
          },
        },
        {
          name: 'metric_1',
          x: [0, 1],
          y: [300, 400],
          type: 'scatter',
          mode: 'lines',
          line: {
            shape: 'spline',
            smoothing: 0,
          },
        },
      ],
    });
  });

  test('getPlotPropsForBarChart()', () => {
    wrapper = shallow(<MetricsPlotView {...minimalPropsForBarChart}/>);
    instance = wrapper.instance();
    expect(instance.getPlotPropsForBarChart()).toEqual({
      data: [
        {
          name: 'RunDisplayName1',
          x: ['metric_0'],
          y: [100],
          type: 'bar',
        },
        {
          name: 'RunDisplayName2',
          x: ['metric_0'],
          y: [300],
          type: 'bar',
        },
      ],
      layout: {
        barmode: 'group',
      },
    });
  });

  test('getLineLegend()', () => {
    expect(MetricsPlotView.getLineLegend('metric_1', 'Run abc', true)).toBe('metric_1, Run abc');
    expect(MetricsPlotView.getLineLegend('metric_1', 'Run abc', false)).toBe('metric_1');
  });

  test('parseTimestamp()', () => {
    const timestamp = 1556662044000;
    const timestampStr = '2019-04-30 15:07:24';
    const history = [{ timestamp: 1556662043000 }];
    expect(MetricsPlotView.parseTimestamp(timestamp, history, X_AXIS_RELATIVE)).toBe(1);
    expect(MetricsPlotView.parseTimestamp(timestamp, history, X_AXIS_WALL)).toBe(timestampStr);
  });
});
