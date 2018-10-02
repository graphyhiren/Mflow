import React from 'react';
import Utils from "../utils/Utils";
import { Link } from 'react-router-dom';
import Routes from '../Routes';
import classNames from 'classnames';
import { DEFAULT_EXPANDED_VALUE } from './ExperimentView';


const styles = {
  sortIconStyle: {
    verticalAlign: "middle",
    fontSize: 20,
  },
  headerCellText: {
    verticalAlign: "middle"
  },
  sortIconContainer: {
    marginLeft: 2,
    minWidth: 12.5,
    display: 'inline-block',
  },
};

function getSortIconHelper(sortState) {
    return (<span><i
      className={sortState.ascending ? "fas fa-caret-up" : "fas fa-caret-down"}
      style={styles.sortIconStyle}
    /></span>);
}

export default class ExperimentViewUtil {
  /** Returns checkbox cell for a row. */
  static getCheckboxForRow(selected, checkboxHandler) {
    return <td key="meta-check">
      <div>
        <input type="checkbox" checked={selected} onClick={checkboxHandler}/>
      </div>
    </td>;
  }

  /**
   * Returns table cells describing run metadata (i.e. not params/metrics) comprising part of
   * the display row for a run.
   */
  static getRunInfoCellsForRow(runInfo, tags, isParent) {
    const user = Utils.formatUser(runInfo.user_id);
    const sourceType = Utils.renderSource(runInfo, tags);
    const startTime = runInfo.start_time;
    const childLeftMargin = isParent ? {} : {paddingLeft: '16px'};
    return [
      <td key="meta-link" className="run-table-container" style={{whiteSpace: "inherit"}}>
        <div style={childLeftMargin}>
          <Link to={Routes.getRunPageRoute(runInfo.experiment_id, runInfo.run_uuid)}>
            {Utils.formatTimestamp(startTime)}
          </Link>
        </div>
      </td>,
      <td key="meta-user" className="run-table-container" title={user}>
        <div>
          {user}
        </div>
      </td>,
      <td className="run-table-container" key="meta-source" title={sourceType}>
        <div>
          {Utils.renderSourceTypeIcon(runInfo.source_type)}
          {sourceType}
        </div>
      </td>,
      <td className="run-table-container" key="meta-version">
        <div>
          {Utils.renderVersion(runInfo)}
        </div>
      </td>,
    ];
  }

  /**
   * Returns an icon for sorting the metric or param column with the specified key. The icon
   * is visible if we're currently sorting by the corresponding column. Otherwise, the icon is
   * invisible but takes up space.
   */
  static getSortIcon(sortState, isMetric, isParam, key) {
    if (ExperimentViewUtil.isSortedBy(sortState, isMetric, isParam, key)) {
      return getSortIconHelper(sortState);
    }
  }

  /** Returns checkbox element for selecting all runs */
  static getSelectAllCheckbox(onCheckAll, isAllCheckedBool) {
    return <th key="meta-check" className="bottom-row">
      <input type="checkbox" onChange={onCheckAll} checked={isAllCheckedBool} />
    </th>;
  }

  /**
   * Returns header-row table cells for columns containing run metadata.
   */
  static getRunMetadataHeaderCells(onSortBy, sortState) {
    const getHeaderCell = (key, text) => {
      const sortIcon = ExperimentViewUtil.getSortIcon(sortState, false, false, key);
      return (
        <th
          key={"meta-" + key}
          className="bottom-row sortable run-table-container"
          onClick={() => onSortBy(false, false, key)}
        >
          <span style={styles.headerCellText}>{text}</span>
          <span style={styles.sortIconContainer}>{sortIcon}</span>
        </th>);
    };
    return [
      getHeaderCell("start_time", <span>{"Date"}</span>),
      getHeaderCell("user_id", <span>{"User"}</span>),
      getHeaderCell("source", <span>{"Source"}</span>),
      getHeaderCell("source_version", <span>{"Version"}</span>),
    ];
  }

  static getExpanderHeader() {
    return <th
      key={"meta-expander"}
      className={"bottom-row run-table-container"}
      style={{width: '5px'}}
    />;
  }

  static isSortedBy(sortState, isMetric, isParam, key) {
    return (sortState.isMetric === isMetric && sortState.isParam === isParam
      && sortState.key === key);
  }

  static computeMetricRanges(metricsByRun) {
    const ret = {};
    metricsByRun.forEach(metrics => {
      metrics.forEach(metric => {
        if (!ret.hasOwnProperty(metric.key)) {
          ret[metric.key] = {min: Math.min(metric.value, metric.value * 0.7), max: metric.value};
        } else {
          if (metric.value < ret[metric.key].min) {
            ret[metric.key].min = Math.min(metric.value, metric.value * 0.7);
          }
          if (metric.value > ret[metric.key].max) {
            ret[metric.key].max = metric.value;
          }
        }
      });
    });
    return ret;
  }

  /**
   * Turn a list of metrics to a map of metric key to metric.
   */
  static toMetricsMap(metrics) {
    const ret = {};
    metrics.forEach((metric) => {
      ret[metric.key] = metric;
    });
    return ret;
  }

  /**
   * Turn a list of metrics to a map of metric key to metric.
   */
  static toParamsMap(params) {
    const ret = {};
    params.forEach((param) => {
      ret[param.key] = param;
    });
    return ret;
  }

  /**
   * Mutates and sorts the rows by the sortValue member.
   */
  static sortRows(rows, sortState) {
    rows.sort((a, b) => {
      if (a.sortValue === undefined) {
        return 1;
      } else if (b.sortValue === undefined) {
        return -1;
      } else if (!sortState.ascending) {
        // eslint-disable-next-line no-param-reassign
        [a, b] = [b, a];
      }
      let x = a.sortValue;
      let y = b.sortValue;
      // Casting to number if possible
      if (!isNaN(+x)) {
        x = +x;
      }
      if (!isNaN(+y)) {
        y = +y;
      }
      return x < y ? -1 : (x > y ? 1 : 0);
    });
  }

  /**
   * Computes the sortValue for this row
   */
  static computeSortValue(sortState, metricsMap, paramsMap, runInfo, tags) {
    if (sortState.isMetric || sortState.isParam) {
      const sortValue = (sortState.isMetric ? metricsMap : paramsMap)[sortState.key];
      return (sortValue === undefined ? undefined : sortValue.value);
    } else if (sortState.key === 'user_id') {
      return Utils.formatUser(runInfo.user_id);
    } else if (sortState.key === 'source') {
      return Utils.formatSource(runInfo, tags);
    } else {
      return runInfo[sortState.key];
    }
  }

  static isExpanderOpen(runsExpanded, runId) {
    let expanderOpen = DEFAULT_EXPANDED_VALUE;
    if (runsExpanded[runId] !== undefined) expanderOpen = runsExpanded[runId];
    return expanderOpen;
  }

  static getExpander(hasExpander, expanderOpen, onExpandBound) {
    if (!hasExpander) {
      return <td>
      </td>;
    }
    if (expanderOpen) {
      return (
        <td onClick={onExpandBound}><i className="far fa-minus-square"/></td>
      );
    } else {
      return (
        <td onClick={onExpandBound}><i className="far fa-plus-square"/></td>
      );
    }
  }

  static getRows({ runInfos, sortState, tagsList, runsExpanded, getRow }) {
    const runIdToIdx = {};
    runInfos.forEach((r, idx) => {
      runIdToIdx[r.run_uuid] = idx;
    });
    const treeNodes = runInfos.map(r => new TreeNode(r.run_uuid));
    tagsList.forEach((tags, idx) => {
      const parentRunId = tags['mlflow.parentRunId'];
      if (parentRunId) {
        const parentRunIdx = runIdToIdx[parentRunId.value];
        if (parentRunIdx !== undefined) {
          treeNodes[idx].parent = treeNodes[parentRunIdx];
        }
      }
    });
    // Map of parentRunIds to list of children runs (idx)
    const parentIdToChildren = {};
    treeNodes.forEach((t, idx) => {
      const root = t.findRoot();
      if (root !== undefined && root.value !== t.value) {
        const old = parentIdToChildren[root.value];
        parentIdToChildren[root.value] = old ? (old.push(idx)) : [idx];
      }
    });
    const parentRows = [...Array(runInfos.length).keys()].flatMap((idx) => {
      if (!treeNodes[idx].isRoot() || treeNodes[idx].isCycle()) return [];
      const runId = runInfos[idx].run_uuid;
      let hasExpander = false;
      let childrenIds = undefined;
      if (parentIdToChildren[runId]) {
        hasExpander = true;
        childrenIds = parentIdToChildren[runId].map((cIdx => runInfos[cIdx].run_uuid));
      }
      return [getRow({
        idx,
        isParent: true,
        hasExpander,
        expanderOpen: ExperimentViewUtil.isExpanderOpen(runsExpanded, runId),
        childrenIds,
      })];
    });
    ExperimentViewUtil.sortRows(parentRows, sortState);
    const mergedRows = [];
    parentRows.forEach((r) => {
      const runId = r.key;
      mergedRows.push(r);
      const childrenIdxs = parentIdToChildren[runId];
      if (childrenIdxs) {
        const isHidden = !ExperimentViewUtil.isExpanderOpen(runsExpanded, runId);
        const childrenRows = childrenIdxs.map((idx) =>
          getRow({ idx, isParent: false, hasExpander: false, isHidden }));
        ExperimentViewUtil.sortRows(childrenRows, sortState);
        mergedRows.push(...childrenRows);
      }
    });
    return mergedRows;
  }

  static renderRows(rows) {
    return rows.map(row => {
      const style = row.isChild ? { backgroundColor: "#fafafa" } : {};
      return (
        <tr
          key={row.key}
          style={style}
          className={classNames('ExperimentView-row', {'ExperimentView-hiddenRow': row.isHidden})}
        >
          {row.contents}
        </tr>
      );
    });
  }
}

class TreeNode {
  constructor(value) {
    this.value = value;
    this.parent = undefined;
  }
  /**
   * Returns the root node. If there is a cycle it will return undefined;
   */
  findRoot() {
    const visited = new Set([this.value]);
    let current = this;
    while (current.parent !== undefined) {
      if (visited.has(current.parent.value)) {
        return undefined;
      }
      current = current.parent;
    }
    return current;
  }
  isRoot() {
    return this.findRoot().value === this.value;
  }
  isCycle() {
    return this.findRoot() === undefined;
  }
}