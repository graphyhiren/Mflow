/**
 * NOTE: this code file was automatically migrated to TypeScript using ts-migrate and
 * may contain multiple `any` type annotations and `@ts-expect-error` directives.
 * If possible, please improve types while making changes to this file. If the type
 * annotations are already looking good, please remove this comment.
 */

import React from 'react';
import { Typography } from '@databricks/design-system';
import { Table } from 'antd';
import { LogModelWithSignatureUrl } from '../../common/constants';
import { gray800 } from '../../common/styles/color';
import { spacingMedium } from '../../common/styles/spacing';
import { ColumnSpec, TensorSpec, ColumnType } from '../types/model-schema';
import { FormattedMessage, injectIntl } from 'react-intl';

const { Column } = Table;
const { Text } = Typography;
const INDENTATION_SPACES = 2;

type Props = {
  schema?: any;
  defaultExpandAllRows?: boolean;
  intl: {
    formatMessage: (...args: any[]) => any;
  };
};

// return a formatted string representation of the column type
function getColumnTypeRepr(columnType: ColumnType, indentationLevel: number): string {
  const { type } = columnType;

  const indentation = ' '.repeat(indentationLevel * INDENTATION_SPACES);
  if (type === 'object') {
    const propertyReprs = Object.keys(columnType.properties).map((propertyName) => {
      const property = columnType.properties[propertyName];
      const requiredRepr = property.required ? '' : ' (optional)';
      const propertyRepr = getColumnTypeRepr(property, indentationLevel + 1);
      const indentOffset = (indentationLevel + 1) * INDENTATION_SPACES;

      return `${' '.repeat(indentOffset)}${propertyName}: ${
        propertyRepr.slice(indentOffset) + requiredRepr
      }`;
    });

    return `${indentation}{\n${propertyReprs.join(',\n')}\n${indentation}}`;
  }

  if (type === 'array') {
    const indentOffset = indentationLevel * INDENTATION_SPACES;
    const itemsTypeRepr = getColumnTypeRepr(columnType.items, indentationLevel).slice(indentOffset);
    return `${indentation}Array(${itemsTypeRepr})`;
  }

  return `${indentation}${type}`;
}

function formatColumnName(spec: ColumnSpec | TensorSpec): React.ReactElement {
  let required = true;
  if (spec.required !== undefined) {
    ({ required } = spec);
  } else if (spec.optional !== undefined && spec.optional) {
    required = false;
  }
  const requiredTag = required ? (
    <Text bold>{'(required)'}</Text>
  ) : (
    <Text color='secondary'>{'(optional)'}</Text>
  );

  const name = 'name' in spec ? spec.name : '-';

  return (
    <Text>
      {name} {requiredTag}
    </Text>
  );
}

function formatColumnSchema(spec: ColumnSpec | TensorSpec): React.ReactElement {
  let repr = '';
  if (spec.type === 'tensor') {
    repr = `Tensor (dtype: ${spec['tensor-spec'].dtype}, shape: [${spec['tensor-spec'].shape}])`;
  } else {
    repr = getColumnTypeRepr(spec, 0);
  }

  return (
    <pre
      style={{
        padding: 8,
        marginTop: 8,
        marginBottom: 8,
        whiteSpace: 'pre-wrap',
      }}
    >
      {repr}
    </pre>
  );
}

export class SchemaTableImpl extends React.PureComponent<Props> {
  renderSchemaTable = (schemaData: any, schemaType: any) => {
    const columns = [
      {
        title: 'Name',
        dataIndex: 'name',
        key: 'name',
        width: '40%',
      },
      {
        title: 'Type',
        dataIndex: 'type',
        key: 'type',
        width: '60%',
      },
    ];

    return (
      <Table
        className='inner-table'
        size='middle'
        showHeader={false}
        pagination={false}
        locale={{ emptyText: `No schema ${schemaType}.` }}
        dataSource={this.getSchemaRowData(schemaData)}
        columns={columns}
        scroll={{ y: 240 }}
      />
    );
  };

  getSchemaTypeRepr = (schemaTypeSpec: ColumnSpec | TensorSpec): string => {
    const { type } = schemaTypeSpec;

    let repr: string = type;
    if (schemaTypeSpec.type === 'tensor') {
      repr = `Tensor (dtype: ${schemaTypeSpec['tensor-spec'].dtype}, shape: [${schemaTypeSpec['tensor-spec'].shape}])`;
    } else {
      repr = getColumnTypeRepr(schemaTypeSpec, 0);
    }

    // If the "optional" property is present and true, wrap the type around an "Optional[]"
    // NOTE: newer model signatures will have "required" instead of "optional", but we currently
    // have to support both since both exist.
    if (schemaTypeSpec.optional) {
      repr = `Optional[${repr}]`;
    }

    return repr;
  };

  getSchemaRowData = (schemaData: any) => {
    const rowData: any = [];
    schemaData.forEach((row: any, index: any) => {
      rowData[index] = {
        key: index,
        name: formatColumnName(row),
        type: formatColumnSchema(row),
      };
    });
    return rowData;
  };

  renderSectionHeader = (text: any) => {
    return <strong className='primary-text'>{text}</strong>;
  };

  render() {
    const { schema } = this.props;
    const hasSchema = schema.inputs.length || schema.outputs.length;
    const sectionHeaders = hasSchema
      ? [
          {
            key: '1',
            name: this.props.intl.formatMessage(
              {
                defaultMessage: 'Inputs ({numInputs})',
                description: 'Input section header for schema table in model version page',
              },
              {
                numInputs: schema.inputs.length,
              },
            ),
            type: '',
            table: this.renderSchemaTable(schema.inputs, 'inputs'),
          },
          {
            key: '2',
            name: this.props.intl.formatMessage(
              {
                defaultMessage: 'Outputs ({numOutputs})',
                description: 'Input section header for schema table in model version page',
              },
              {
                numOutputs: schema.outputs.length,
              },
            ),
            type: '',
            table: this.renderSchemaTable(schema.outputs, 'outputs'),
          },
        ]
      : [];

    return (
      // @ts-expect-error TS(2322): Type '{ [x: string]: { padding: string; width: str... Remove this comment to see the full error message
      <div css={schemaTableStyles}>
        <Table
          key='schema-table'
          className='outer-table'
          rowClassName='section-header-row'
          size='middle'
          pagination={false}
          defaultExpandAllRows={this.props.defaultExpandAllRows}
          expandRowByClick
          expandedRowRender={(record) => record.table}
          expandIcon={({ expanded, onExpand, record }) =>
            expanded ? (
              <span onClick={(e) => onExpand(record, e)}>
                <i className='far fa-minus-square' />
              </span>
            ) : (
              <span onClick={(e) => onExpand(record, e)}>
                <i className='far fa-plus-square' />
              </span>
            )
          }
          locale={{
            emptyText: (
              <div>
                {/* eslint-disable-next-line max-len */}
                <FormattedMessage
                  defaultMessage='No schema. See <link>MLflow docs</link> for how to include
                     input and output schema with your model.'
                  description='Text for schema table when no schema exists in the model version
                     page'
                  values={{
                    link: (chunks: any) => (
                      <a href={LogModelWithSignatureUrl} target='_blank' rel='noreferrer'>
                        {chunks}
                      </a>
                    ),
                  }}
                />
              </div>
            ),
          }}
          dataSource={sectionHeaders}
          scroll={{ x: 240 }}
        >
          <Column
            key={1}
            title={this.props.intl.formatMessage({
              defaultMessage: 'Name',
              description: 'Text for name column in schema table in model version page',
            })}
            width='40%'
            dataIndex='name'
            render={this.renderSectionHeader}
          />
          <Column
            key={2}
            title={this.props.intl.formatMessage({
              defaultMessage: 'Type',
              description: 'Text for type column in schema table in model version page',
            })}
            width='60%'
            dataIndex='type'
            render={this.renderSectionHeader}
          />
        </Table>
      </div>
    );
  }
}

// @ts-expect-error TS(2769): No overload matches this call.
export const SchemaTable = injectIntl(SchemaTableImpl);

const antTable = '.ant-table-middle>.ant-table-content>.ant-table-scroll>.ant-table-body>table';
const schemaTableStyles = {
  [`${antTable}>.ant-table-thead>tr>th.ant-table-expand-icon-th`]: {
    padding: `${spacingMedium}px 0`,
    width: '32px',
  },
  [`${antTable}>.ant-table-thead>tr>th.ant-table-row-cell-break-word`]: {
    padding: `${spacingMedium}px 0`,
  },
  [`${antTable}>.ant-table-tbody>tr>td.ant-table-row-cell-break-word`]: {
    padding: `${spacingMedium}px 0`,
  },
  [`${antTable}>.ant-table-tbody>tr.section-header-row>td.ant-table-row-cell-break-word`]: {
    padding: '0',
    backgroundColor: '#EEEEEE',
    width: '32px',
  },
  [`${antTable}>.ant-table-tbody>tr.section-header-row>td.ant-table-row-expand-icon-cell`]: {
    padding: '0',
    backgroundColor: '#EEEEEE',
  },
  '.outer-table .ant-table-body': {
    // !important to override inline style of overflowX: scroll
    overflowX: 'auto !important',
    overflowY: 'hidden',
  },
  '.inner-table .ant-table-body': {
    // !important to override inline style of overflowY: scroll
    overflowY: 'auto !important',
  },
  '.ant-table-expanded-row td': {
    backgroundColor: 'white',
  },
  '.inner-table': {
    maxWidth: 800,
  },
  '.outer-table': {
    maxWidth: 800,
  },
  '.primary-text': {
    color: gray800,
  },
  '.section-header-row': {
    lineHeight: '32px',
    cursor: 'pointer',
  },
};
