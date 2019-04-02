package org.mlflow.tracking;

import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.MessageOrBuilder;
import com.google.protobuf.util.JsonFormat;

import java.lang.Iterable;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.mlflow.api.proto.Service.*;

class MlflowProtobufMapper {

  String makeCreateExperimentRequest(String expName) {
    CreateExperiment.Builder builder = CreateExperiment.newBuilder();
    builder.setName(expName);
    return print(builder);
  }

  String makeDeleteExperimentRequest(long experimentId) {
    DeleteExperiment.Builder builder = DeleteExperiment.newBuilder();
    builder.setExperimentId(experimentId);
    return print(builder);
  }

  String makeRestoreExperimentRequest(long experimentId) {
    RestoreExperiment.Builder builder = RestoreExperiment.newBuilder();
    builder.setExperimentId(experimentId);
    return print(builder);
  }

  String makeUpdateExperimentRequest(long experimentId, String newExperimentName) {
    UpdateExperiment.Builder builder = UpdateExperiment.newBuilder();
    builder.setExperimentId(experimentId);
    builder.setNewName(newExperimentName);
    return print(builder);
  }

  String makeLogParam(String runUuid, String key, String value) {
    LogParam.Builder builder = LogParam.newBuilder();
    builder.setRunUuid(runUuid);
    builder.setKey(key);
    builder.setValue(value);
    return print(builder);
  }

  String makeLogMetric(String runUuid, String key, double value, long timestamp) {
    LogMetric.Builder builder = LogMetric.newBuilder();
    builder.setRunUuid(runUuid);
    builder.setKey(key);
    builder.setValue(value);
    builder.setTimestamp(timestamp);
    return print(builder);
  }

  String makeSetTag(String runUuid, String key, String value) {
    SetTag.Builder builder = SetTag.newBuilder();
    builder.setRunUuid(runUuid);
    builder.setKey(key);
    builder.setValue(value);
    return print(builder);
  }

  String makeLogBatch(String runUuid,
      Iterable<Metric> metrics,
      Iterable<Param> params,
      Iterable<RunTag> tags) {
    LogBatch.Builder builder = LogBatch.newBuilder();
    builder.setRunId(runUuid);
    if (metrics != null) {
      builder.addAllMetrics(metrics);
    }
    if (params != null) {
      builder.addAllParams(params);
    }
    if (tags != null) {
      builder.addAllTags(tags);
    }
    return print(builder);
  }


  public static Metric createMetric(String name, double value, long timestamp) {
    Metric.Builder builder = Metric.newBuilder();
    builder.setKey(name).setValue(value).setTimestamp(timestamp);
    return builder.build();
  }

  List<Metric> makeMetricList(Map<String, Double> metrics) {
    long timestamp = System.currentTimeMillis();
    List<Metric> metricList = new ArrayList<>();
    for (Map.Entry<String, Double> entry: metrics.entrySet()) {
      metricList.add(createMetric(entry.getKey(), entry.getValue(), timestamp));
    }
    return metricList;
  }

  public static Param createParam(String name, String value) {
    Param.Builder builder = Param.newBuilder();
    builder.setKey(name).setValue(value);
    return builder.build();
  }

  List<Param> makeParamList(Map<String, String> params) {
    List<Param> paramList = new ArrayList<>();
    for (Map.Entry<String, String> entry : params.entrySet()) {
      paramList.add(createParam(entry.getKey(), entry.getValue()));
    }
    return paramList;
  }

  public static RunTag createTag(String name, String value) {
    RunTag.Builder builder = RunTag.newBuilder();
    builder.setKey(name).setValue(value);
    return builder.build();
  }

  List<RunTag> makeTagList(Map<String, String> params) {
    List<RunTag> tagList = new ArrayList<>();
    for (Map.Entry<String, String> entry : params.entrySet()) {
      tagList.add(createTag(entry.getKey(), entry.getValue()));
    }
    return tagList;
  }

  String makeUpdateRun(String runUuid, RunStatus status, long endTime) {
    UpdateRun.Builder builder = UpdateRun.newBuilder();
    builder.setRunUuid(runUuid);
    builder.setStatus(status);
    builder.setEndTime(endTime);
    return print(builder);
  }

  String makeDeleteRun(String runUuid) {
    DeleteRun.Builder builder = DeleteRun.newBuilder();
    builder.setRunId(runUuid);
    return print(builder);
  }

  String makeRestoreRun(String runUuid) {
    RestoreRun.Builder builder = RestoreRun.newBuilder();
    builder.setRunId(runUuid);
    return print(builder);
  }

  String toJson(MessageOrBuilder mb) {
    return print(mb);
  }

  GetExperiment.Response toGetExperimentResponse(String json) {
    GetExperiment.Response.Builder builder = GetExperiment.Response.newBuilder();
    merge(json, builder);
    return builder.build();
  }

  ListExperiments.Response toListExperimentsResponse(String json) {
    ListExperiments.Response.Builder builder = ListExperiments.Response.newBuilder();
    merge(json, builder);
    return builder.build();
  }

  CreateExperiment.Response toCreateExperimentResponse(String json) {
    CreateExperiment.Response.Builder builder = CreateExperiment.Response.newBuilder();
    merge(json, builder);
    return builder.build();
  }

  GetRun.Response toGetRunResponse(String json) {
    GetRun.Response.Builder builder = GetRun.Response.newBuilder();
    merge(json, builder);
    return builder.build();
  }

  CreateRun.Response toCreateRunResponse(String json) {
    CreateRun.Response.Builder builder = CreateRun.Response.newBuilder();
    merge(json, builder);
    return builder.build();
  }

  SearchRuns.Response toSearchRunsResponse(String json) {
    SearchRuns.Response.Builder builder = SearchRuns.Response.newBuilder();
    merge(json, builder);
    return builder.build();
  }

  private String print(MessageOrBuilder message) {
    try {
      return JsonFormat.printer().preservingProtoFieldNames().print(message);
    } catch (InvalidProtocolBufferException e) {
      throw new MlflowClientException("Failed to serialize message " + message, e);
    }
  }

  private void merge(String json, com.google.protobuf.Message.Builder builder) {
    try {
      JsonFormat.parser().ignoringUnknownFields().merge(json, builder);
    } catch (InvalidProtocolBufferException e) {
      throw new MlflowClientException("Failed to serialize json " + json + " into " + builder, e);
    }
  }
}
