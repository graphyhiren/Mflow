
import google.protobuf
from packaging.version import Version
if Version(google.protobuf.__version__) >= Version("5.26.0"):
  # -*- coding: utf-8 -*-
  # Generated by the protocol buffer compiler.  DO NOT EDIT!
  # source: facet_feature_statistics.proto
  # Protobuf Python Version: 5.26.0
  """Generated protocol buffer code."""
  from google.protobuf import descriptor as _descriptor
  from google.protobuf import descriptor_pool as _descriptor_pool
  from google.protobuf import symbol_database as _symbol_database
  from google.protobuf.internal import builder as _builder
  # @@protoc_insertion_point(imports)
  
  _sym_db = _symbol_database.Default()
  
  
  
  
  DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x66\x61\x63\x65t_feature_statistics.proto\x12\x16\x66\x61\x63\x65tFeatureStatistics\"b\n\x1c\x44\x61tasetFeatureStatisticsList\x12\x42\n\x08\x64\x61tasets\x18\x01 \x03(\x0b\x32\x30.facetFeatureStatistics.DatasetFeatureStatistics\"\x14\n\x04Path\x12\x0c\n\x04step\x18\x01 \x03(\t\"\x9e\x01\n\x18\x44\x61tasetFeatureStatistics\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0cnum_examples\x18\x02 \x01(\x03\x12\x1d\n\x15weighted_num_examples\x18\x04 \x01(\x01\x12?\n\x08\x66\x65\x61tures\x18\x03 \x03(\x0b\x32-.facetFeatureStatistics.FeatureNameStatistics\"\xae\x04\n\x15\x46\x65\x61tureNameStatistics\x12\x0e\n\x04name\x18\x01 \x01(\tH\x00\x12,\n\x04path\x18\x08 \x01(\x0b\x32\x1c.facetFeatureStatistics.PathH\x00\x12@\n\x04type\x18\x02 \x01(\x0e\x32\x32.facetFeatureStatistics.FeatureNameStatistics.Type\x12>\n\tnum_stats\x18\x03 \x01(\x0b\x32).facetFeatureStatistics.NumericStatisticsH\x01\x12@\n\x0cstring_stats\x18\x04 \x01(\x0b\x32(.facetFeatureStatistics.StringStatisticsH\x01\x12>\n\x0b\x62ytes_stats\x18\x05 \x01(\x0b\x32\'.facetFeatureStatistics.BytesStatisticsH\x01\x12@\n\x0cstruct_stats\x18\x07 \x01(\x0b\x32(.facetFeatureStatistics.StructStatisticsH\x01\x12=\n\x0c\x63ustom_stats\x18\x06 \x03(\x0b\x32\'.facetFeatureStatistics.CustomStatistic\"=\n\x04Type\x12\x07\n\x03INT\x10\x00\x12\t\n\x05\x46LOAT\x10\x01\x12\n\n\x06STRING\x10\x02\x12\t\n\x05\x42YTES\x10\x03\x12\n\n\x06STRUCT\x10\x04\x42\n\n\x08\x66ield_idB\x07\n\x05stats\"x\n\x18WeightedCommonStatistics\x12\x17\n\x0fnum_non_missing\x18\x01 \x01(\x01\x12\x13\n\x0bnum_missing\x18\x02 \x01(\x01\x12\x16\n\x0e\x61vg_num_values\x18\x03 \x01(\x01\x12\x16\n\x0etot_num_values\x18\x04 \x01(\x01\"\xc3\x01\n\x0f\x43ustomStatistic\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x03num\x18\x02 \x01(\x01H\x00\x12\r\n\x03str\x18\x03 \x01(\tH\x00\x12\x36\n\thistogram\x18\x04 \x01(\x0b\x32!.facetFeatureStatistics.HistogramH\x00\x12?\n\x0erank_histogram\x18\x05 \x01(\x0b\x32%.facetFeatureStatistics.RankHistogramH\x00\x42\x05\n\x03valJ\x04\x08\x06\x10\x07\"\xb9\x02\n\x11NumericStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\x12\x0c\n\x04mean\x18\x02 \x01(\x01\x12\x0f\n\x07std_dev\x18\x03 \x01(\x01\x12\x11\n\tnum_zeros\x18\x04 \x01(\x03\x12\x0b\n\x03min\x18\x05 \x01(\x01\x12\x0e\n\x06median\x18\x06 \x01(\x01\x12\x0b\n\x03max\x18\x07 \x01(\x01\x12\x35\n\nhistograms\x18\x08 \x03(\x0b\x32!.facetFeatureStatistics.Histogram\x12Q\n\x16weighted_numeric_stats\x18\t \x01(\x0b\x32\x31.facetFeatureStatistics.WeightedNumericStatistics\"\xa0\x03\n\x10StringStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\x12\x0e\n\x06unique\x18\x02 \x01(\x03\x12I\n\ntop_values\x18\x03 \x03(\x0b\x32\x35.facetFeatureStatistics.StringStatistics.FreqAndValue\x12\x12\n\navg_length\x18\x04 \x01(\x02\x12=\n\x0erank_histogram\x18\x05 \x01(\x0b\x32%.facetFeatureStatistics.RankHistogram\x12O\n\x15weighted_string_stats\x18\x06 \x01(\x0b\x32\x30.facetFeatureStatistics.WeightedStringStatistics\x1aM\n\x0c\x46reqAndValue\x12\x1b\n\x0f\x64\x65precated_freq\x18\x01 \x01(\x03\x42\x02\x18\x01\x12\r\n\x05value\x18\x02 \x01(\t\x12\x11\n\tfrequency\x18\x03 \x01(\x01\"\x81\x01\n\x19WeightedNumericStatistics\x12\x0c\n\x04mean\x18\x01 \x01(\x01\x12\x0f\n\x07std_dev\x18\x02 \x01(\x01\x12\x0e\n\x06median\x18\x03 \x01(\x01\x12\x35\n\nhistograms\x18\x04 \x03(\x0b\x32!.facetFeatureStatistics.Histogram\"\xa4\x01\n\x18WeightedStringStatistics\x12I\n\ntop_values\x18\x01 \x03(\x0b\x32\x35.facetFeatureStatistics.StringStatistics.FreqAndValue\x12=\n\x0erank_histogram\x18\x02 \x01(\x0b\x32%.facetFeatureStatistics.RankHistogram\"\xac\x01\n\x0f\x42ytesStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\x12\x0e\n\x06unique\x18\x02 \x01(\x03\x12\x15\n\ravg_num_bytes\x18\x03 \x01(\x02\x12\x15\n\rmin_num_bytes\x18\x04 \x01(\x02\x12\x15\n\rmax_num_bytes\x18\x05 \x01(\x02J\x04\x08\x06\x10\x07\"R\n\x10StructStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\"\x88\x03\n\x10\x43ommonStatistics\x12\x17\n\x0fnum_non_missing\x18\x01 \x01(\x03\x12\x13\n\x0bnum_missing\x18\x02 \x01(\x03\x12\x16\n\x0emin_num_values\x18\x03 \x01(\x03\x12\x16\n\x0emax_num_values\x18\x04 \x01(\x03\x12\x16\n\x0e\x61vg_num_values\x18\x05 \x01(\x02\x12\x16\n\x0etot_num_values\x18\x08 \x01(\x03\x12?\n\x14num_values_histogram\x18\x06 \x01(\x0b\x32!.facetFeatureStatistics.Histogram\x12O\n\x15weighted_common_stats\x18\x07 \x01(\x0b\x32\x30.facetFeatureStatistics.WeightedCommonStatistics\x12H\n\x1d\x66\x65\x61ture_list_length_histogram\x18\t \x01(\x0b\x32!.facetFeatureStatistics.HistogramJ\x04\x08\n\x10\x0bJ\x04\x08\x0b\x10\x0c\"\xce\x02\n\tHistogram\x12\x0f\n\x07num_nan\x18\x01 \x01(\x03\x12\x15\n\rnum_undefined\x18\x02 \x01(\x03\x12\x39\n\x07\x62uckets\x18\x03 \x03(\x0b\x32(.facetFeatureStatistics.Histogram.Bucket\x12=\n\x04type\x18\x04 \x01(\x0e\x32/.facetFeatureStatistics.Histogram.HistogramType\x12\x0c\n\x04name\x18\x05 \x01(\t\x1a\x63\n\x06\x42ucket\x12\x11\n\tlow_value\x18\x01 \x01(\x01\x12\x12\n\nhigh_value\x18\x02 \x01(\x01\x12\x1c\n\x10\x64\x65precated_count\x18\x03 \x01(\x03\x42\x02\x18\x01\x12\x14\n\x0csample_count\x18\x04 \x01(\x01\",\n\rHistogramType\x12\x0c\n\x08STANDARD\x10\x00\x12\r\n\tQUANTILES\x10\x01\"\xce\x01\n\rRankHistogram\x12=\n\x07\x62uckets\x18\x01 \x03(\x0b\x32,.facetFeatureStatistics.RankHistogram.Bucket\x12\x0c\n\x04name\x18\x02 \x01(\t\x1ap\n\x06\x42ucket\x12\x10\n\x08low_rank\x18\x01 \x01(\x03\x12\x11\n\thigh_rank\x18\x02 \x01(\x03\x12\x1c\n\x10\x64\x65precated_count\x18\x03 \x01(\x03\x42\x02\x18\x01\x12\r\n\x05label\x18\x04 \x01(\t\x12\x14\n\x0csample_count\x18\x05 \x01(\x01')
  
  _globals = globals()
  _builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
  _builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'facet_feature_statistics_pb2', _globals)
  if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_STRINGSTATISTICS_FREQANDVALUE'].fields_by_name['deprecated_freq']._loaded_options = None
    _globals['_STRINGSTATISTICS_FREQANDVALUE'].fields_by_name['deprecated_freq']._serialized_options = b'\030\001'
    _globals['_HISTOGRAM_BUCKET'].fields_by_name['deprecated_count']._loaded_options = None
    _globals['_HISTOGRAM_BUCKET'].fields_by_name['deprecated_count']._serialized_options = b'\030\001'
    _globals['_RANKHISTOGRAM_BUCKET'].fields_by_name['deprecated_count']._loaded_options = None
    _globals['_RANKHISTOGRAM_BUCKET'].fields_by_name['deprecated_count']._serialized_options = b'\030\001'
    _globals['_DATASETFEATURESTATISTICSLIST']._serialized_start=58
    _globals['_DATASETFEATURESTATISTICSLIST']._serialized_end=156
    _globals['_PATH']._serialized_start=158
    _globals['_PATH']._serialized_end=178
    _globals['_DATASETFEATURESTATISTICS']._serialized_start=181
    _globals['_DATASETFEATURESTATISTICS']._serialized_end=339
    _globals['_FEATURENAMESTATISTICS']._serialized_start=342
    _globals['_FEATURENAMESTATISTICS']._serialized_end=900
    _globals['_FEATURENAMESTATISTICS_TYPE']._serialized_start=818
    _globals['_FEATURENAMESTATISTICS_TYPE']._serialized_end=879
    _globals['_WEIGHTEDCOMMONSTATISTICS']._serialized_start=902
    _globals['_WEIGHTEDCOMMONSTATISTICS']._serialized_end=1022
    _globals['_CUSTOMSTATISTIC']._serialized_start=1025
    _globals['_CUSTOMSTATISTIC']._serialized_end=1220
    _globals['_NUMERICSTATISTICS']._serialized_start=1223
    _globals['_NUMERICSTATISTICS']._serialized_end=1536
    _globals['_STRINGSTATISTICS']._serialized_start=1539
    _globals['_STRINGSTATISTICS']._serialized_end=1955
    _globals['_STRINGSTATISTICS_FREQANDVALUE']._serialized_start=1878
    _globals['_STRINGSTATISTICS_FREQANDVALUE']._serialized_end=1955
    _globals['_WEIGHTEDNUMERICSTATISTICS']._serialized_start=1958
    _globals['_WEIGHTEDNUMERICSTATISTICS']._serialized_end=2087
    _globals['_WEIGHTEDSTRINGSTATISTICS']._serialized_start=2090
    _globals['_WEIGHTEDSTRINGSTATISTICS']._serialized_end=2254
    _globals['_BYTESSTATISTICS']._serialized_start=2257
    _globals['_BYTESSTATISTICS']._serialized_end=2429
    _globals['_STRUCTSTATISTICS']._serialized_start=2431
    _globals['_STRUCTSTATISTICS']._serialized_end=2513
    _globals['_COMMONSTATISTICS']._serialized_start=2516
    _globals['_COMMONSTATISTICS']._serialized_end=2908
    _globals['_HISTOGRAM']._serialized_start=2911
    _globals['_HISTOGRAM']._serialized_end=3245
    _globals['_HISTOGRAM_BUCKET']._serialized_start=3100
    _globals['_HISTOGRAM_BUCKET']._serialized_end=3199
    _globals['_HISTOGRAM_HISTOGRAMTYPE']._serialized_start=3201
    _globals['_HISTOGRAM_HISTOGRAMTYPE']._serialized_end=3245
    _globals['_RANKHISTOGRAM']._serialized_start=3248
    _globals['_RANKHISTOGRAM']._serialized_end=3454
    _globals['_RANKHISTOGRAM_BUCKET']._serialized_start=3342
    _globals['_RANKHISTOGRAM_BUCKET']._serialized_end=3454
  # @@protoc_insertion_point(module_scope)
  
else:
  # -*- coding: utf-8 -*-
  # Generated by the protocol buffer compiler.  DO NOT EDIT!
  # source: facet_feature_statistics.proto
  """Generated protocol buffer code."""
  from google.protobuf import descriptor as _descriptor
  from google.protobuf import descriptor_pool as _descriptor_pool
  from google.protobuf import message as _message
  from google.protobuf import reflection as _reflection
  from google.protobuf import symbol_database as _symbol_database
  # @@protoc_insertion_point(imports)
  
  _sym_db = _symbol_database.Default()
  
  
  
  
  DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1e\x66\x61\x63\x65t_feature_statistics.proto\x12\x16\x66\x61\x63\x65tFeatureStatistics\"b\n\x1c\x44\x61tasetFeatureStatisticsList\x12\x42\n\x08\x64\x61tasets\x18\x01 \x03(\x0b\x32\x30.facetFeatureStatistics.DatasetFeatureStatistics\"\x14\n\x04Path\x12\x0c\n\x04step\x18\x01 \x03(\t\"\x9e\x01\n\x18\x44\x61tasetFeatureStatistics\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0cnum_examples\x18\x02 \x01(\x03\x12\x1d\n\x15weighted_num_examples\x18\x04 \x01(\x01\x12?\n\x08\x66\x65\x61tures\x18\x03 \x03(\x0b\x32-.facetFeatureStatistics.FeatureNameStatistics\"\xae\x04\n\x15\x46\x65\x61tureNameStatistics\x12\x0e\n\x04name\x18\x01 \x01(\tH\x00\x12,\n\x04path\x18\x08 \x01(\x0b\x32\x1c.facetFeatureStatistics.PathH\x00\x12@\n\x04type\x18\x02 \x01(\x0e\x32\x32.facetFeatureStatistics.FeatureNameStatistics.Type\x12>\n\tnum_stats\x18\x03 \x01(\x0b\x32).facetFeatureStatistics.NumericStatisticsH\x01\x12@\n\x0cstring_stats\x18\x04 \x01(\x0b\x32(.facetFeatureStatistics.StringStatisticsH\x01\x12>\n\x0b\x62ytes_stats\x18\x05 \x01(\x0b\x32\'.facetFeatureStatistics.BytesStatisticsH\x01\x12@\n\x0cstruct_stats\x18\x07 \x01(\x0b\x32(.facetFeatureStatistics.StructStatisticsH\x01\x12=\n\x0c\x63ustom_stats\x18\x06 \x03(\x0b\x32\'.facetFeatureStatistics.CustomStatistic\"=\n\x04Type\x12\x07\n\x03INT\x10\x00\x12\t\n\x05\x46LOAT\x10\x01\x12\n\n\x06STRING\x10\x02\x12\t\n\x05\x42YTES\x10\x03\x12\n\n\x06STRUCT\x10\x04\x42\n\n\x08\x66ield_idB\x07\n\x05stats\"x\n\x18WeightedCommonStatistics\x12\x17\n\x0fnum_non_missing\x18\x01 \x01(\x01\x12\x13\n\x0bnum_missing\x18\x02 \x01(\x01\x12\x16\n\x0e\x61vg_num_values\x18\x03 \x01(\x01\x12\x16\n\x0etot_num_values\x18\x04 \x01(\x01\"\xc3\x01\n\x0f\x43ustomStatistic\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x03num\x18\x02 \x01(\x01H\x00\x12\r\n\x03str\x18\x03 \x01(\tH\x00\x12\x36\n\thistogram\x18\x04 \x01(\x0b\x32!.facetFeatureStatistics.HistogramH\x00\x12?\n\x0erank_histogram\x18\x05 \x01(\x0b\x32%.facetFeatureStatistics.RankHistogramH\x00\x42\x05\n\x03valJ\x04\x08\x06\x10\x07\"\xb9\x02\n\x11NumericStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\x12\x0c\n\x04mean\x18\x02 \x01(\x01\x12\x0f\n\x07std_dev\x18\x03 \x01(\x01\x12\x11\n\tnum_zeros\x18\x04 \x01(\x03\x12\x0b\n\x03min\x18\x05 \x01(\x01\x12\x0e\n\x06median\x18\x06 \x01(\x01\x12\x0b\n\x03max\x18\x07 \x01(\x01\x12\x35\n\nhistograms\x18\x08 \x03(\x0b\x32!.facetFeatureStatistics.Histogram\x12Q\n\x16weighted_numeric_stats\x18\t \x01(\x0b\x32\x31.facetFeatureStatistics.WeightedNumericStatistics\"\xa0\x03\n\x10StringStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\x12\x0e\n\x06unique\x18\x02 \x01(\x03\x12I\n\ntop_values\x18\x03 \x03(\x0b\x32\x35.facetFeatureStatistics.StringStatistics.FreqAndValue\x12\x12\n\navg_length\x18\x04 \x01(\x02\x12=\n\x0erank_histogram\x18\x05 \x01(\x0b\x32%.facetFeatureStatistics.RankHistogram\x12O\n\x15weighted_string_stats\x18\x06 \x01(\x0b\x32\x30.facetFeatureStatistics.WeightedStringStatistics\x1aM\n\x0c\x46reqAndValue\x12\x1b\n\x0f\x64\x65precated_freq\x18\x01 \x01(\x03\x42\x02\x18\x01\x12\r\n\x05value\x18\x02 \x01(\t\x12\x11\n\tfrequency\x18\x03 \x01(\x01\"\x81\x01\n\x19WeightedNumericStatistics\x12\x0c\n\x04mean\x18\x01 \x01(\x01\x12\x0f\n\x07std_dev\x18\x02 \x01(\x01\x12\x0e\n\x06median\x18\x03 \x01(\x01\x12\x35\n\nhistograms\x18\x04 \x03(\x0b\x32!.facetFeatureStatistics.Histogram\"\xa4\x01\n\x18WeightedStringStatistics\x12I\n\ntop_values\x18\x01 \x03(\x0b\x32\x35.facetFeatureStatistics.StringStatistics.FreqAndValue\x12=\n\x0erank_histogram\x18\x02 \x01(\x0b\x32%.facetFeatureStatistics.RankHistogram\"\xac\x01\n\x0f\x42ytesStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\x12\x0e\n\x06unique\x18\x02 \x01(\x03\x12\x15\n\ravg_num_bytes\x18\x03 \x01(\x02\x12\x15\n\rmin_num_bytes\x18\x04 \x01(\x02\x12\x15\n\rmax_num_bytes\x18\x05 \x01(\x02J\x04\x08\x06\x10\x07\"R\n\x10StructStatistics\x12>\n\x0c\x63ommon_stats\x18\x01 \x01(\x0b\x32(.facetFeatureStatistics.CommonStatistics\"\x88\x03\n\x10\x43ommonStatistics\x12\x17\n\x0fnum_non_missing\x18\x01 \x01(\x03\x12\x13\n\x0bnum_missing\x18\x02 \x01(\x03\x12\x16\n\x0emin_num_values\x18\x03 \x01(\x03\x12\x16\n\x0emax_num_values\x18\x04 \x01(\x03\x12\x16\n\x0e\x61vg_num_values\x18\x05 \x01(\x02\x12\x16\n\x0etot_num_values\x18\x08 \x01(\x03\x12?\n\x14num_values_histogram\x18\x06 \x01(\x0b\x32!.facetFeatureStatistics.Histogram\x12O\n\x15weighted_common_stats\x18\x07 \x01(\x0b\x32\x30.facetFeatureStatistics.WeightedCommonStatistics\x12H\n\x1d\x66\x65\x61ture_list_length_histogram\x18\t \x01(\x0b\x32!.facetFeatureStatistics.HistogramJ\x04\x08\n\x10\x0bJ\x04\x08\x0b\x10\x0c\"\xce\x02\n\tHistogram\x12\x0f\n\x07num_nan\x18\x01 \x01(\x03\x12\x15\n\rnum_undefined\x18\x02 \x01(\x03\x12\x39\n\x07\x62uckets\x18\x03 \x03(\x0b\x32(.facetFeatureStatistics.Histogram.Bucket\x12=\n\x04type\x18\x04 \x01(\x0e\x32/.facetFeatureStatistics.Histogram.HistogramType\x12\x0c\n\x04name\x18\x05 \x01(\t\x1a\x63\n\x06\x42ucket\x12\x11\n\tlow_value\x18\x01 \x01(\x01\x12\x12\n\nhigh_value\x18\x02 \x01(\x01\x12\x1c\n\x10\x64\x65precated_count\x18\x03 \x01(\x03\x42\x02\x18\x01\x12\x14\n\x0csample_count\x18\x04 \x01(\x01\",\n\rHistogramType\x12\x0c\n\x08STANDARD\x10\x00\x12\r\n\tQUANTILES\x10\x01\"\xce\x01\n\rRankHistogram\x12=\n\x07\x62uckets\x18\x01 \x03(\x0b\x32,.facetFeatureStatistics.RankHistogram.Bucket\x12\x0c\n\x04name\x18\x02 \x01(\t\x1ap\n\x06\x42ucket\x12\x10\n\x08low_rank\x18\x01 \x01(\x03\x12\x11\n\thigh_rank\x18\x02 \x01(\x03\x12\x1c\n\x10\x64\x65precated_count\x18\x03 \x01(\x03\x42\x02\x18\x01\x12\r\n\x05label\x18\x04 \x01(\t\x12\x14\n\x0csample_count\x18\x05 \x01(\x01')
  
  
  
  _DATASETFEATURESTATISTICSLIST = DESCRIPTOR.message_types_by_name['DatasetFeatureStatisticsList']
  _PATH = DESCRIPTOR.message_types_by_name['Path']
  _DATASETFEATURESTATISTICS = DESCRIPTOR.message_types_by_name['DatasetFeatureStatistics']
  _FEATURENAMESTATISTICS = DESCRIPTOR.message_types_by_name['FeatureNameStatistics']
  _WEIGHTEDCOMMONSTATISTICS = DESCRIPTOR.message_types_by_name['WeightedCommonStatistics']
  _CUSTOMSTATISTIC = DESCRIPTOR.message_types_by_name['CustomStatistic']
  _NUMERICSTATISTICS = DESCRIPTOR.message_types_by_name['NumericStatistics']
  _STRINGSTATISTICS = DESCRIPTOR.message_types_by_name['StringStatistics']
  _STRINGSTATISTICS_FREQANDVALUE = _STRINGSTATISTICS.nested_types_by_name['FreqAndValue']
  _WEIGHTEDNUMERICSTATISTICS = DESCRIPTOR.message_types_by_name['WeightedNumericStatistics']
  _WEIGHTEDSTRINGSTATISTICS = DESCRIPTOR.message_types_by_name['WeightedStringStatistics']
  _BYTESSTATISTICS = DESCRIPTOR.message_types_by_name['BytesStatistics']
  _STRUCTSTATISTICS = DESCRIPTOR.message_types_by_name['StructStatistics']
  _COMMONSTATISTICS = DESCRIPTOR.message_types_by_name['CommonStatistics']
  _HISTOGRAM = DESCRIPTOR.message_types_by_name['Histogram']
  _HISTOGRAM_BUCKET = _HISTOGRAM.nested_types_by_name['Bucket']
  _RANKHISTOGRAM = DESCRIPTOR.message_types_by_name['RankHistogram']
  _RANKHISTOGRAM_BUCKET = _RANKHISTOGRAM.nested_types_by_name['Bucket']
  _FEATURENAMESTATISTICS_TYPE = _FEATURENAMESTATISTICS.enum_types_by_name['Type']
  _HISTOGRAM_HISTOGRAMTYPE = _HISTOGRAM.enum_types_by_name['HistogramType']
  DatasetFeatureStatisticsList = _reflection.GeneratedProtocolMessageType('DatasetFeatureStatisticsList', (_message.Message,), {
    'DESCRIPTOR' : _DATASETFEATURESTATISTICSLIST,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.DatasetFeatureStatisticsList)
    })
  _sym_db.RegisterMessage(DatasetFeatureStatisticsList)
  
  Path = _reflection.GeneratedProtocolMessageType('Path', (_message.Message,), {
    'DESCRIPTOR' : _PATH,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.Path)
    })
  _sym_db.RegisterMessage(Path)
  
  DatasetFeatureStatistics = _reflection.GeneratedProtocolMessageType('DatasetFeatureStatistics', (_message.Message,), {
    'DESCRIPTOR' : _DATASETFEATURESTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.DatasetFeatureStatistics)
    })
  _sym_db.RegisterMessage(DatasetFeatureStatistics)
  
  FeatureNameStatistics = _reflection.GeneratedProtocolMessageType('FeatureNameStatistics', (_message.Message,), {
    'DESCRIPTOR' : _FEATURENAMESTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.FeatureNameStatistics)
    })
  _sym_db.RegisterMessage(FeatureNameStatistics)
  
  WeightedCommonStatistics = _reflection.GeneratedProtocolMessageType('WeightedCommonStatistics', (_message.Message,), {
    'DESCRIPTOR' : _WEIGHTEDCOMMONSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.WeightedCommonStatistics)
    })
  _sym_db.RegisterMessage(WeightedCommonStatistics)
  
  CustomStatistic = _reflection.GeneratedProtocolMessageType('CustomStatistic', (_message.Message,), {
    'DESCRIPTOR' : _CUSTOMSTATISTIC,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.CustomStatistic)
    })
  _sym_db.RegisterMessage(CustomStatistic)
  
  NumericStatistics = _reflection.GeneratedProtocolMessageType('NumericStatistics', (_message.Message,), {
    'DESCRIPTOR' : _NUMERICSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.NumericStatistics)
    })
  _sym_db.RegisterMessage(NumericStatistics)
  
  StringStatistics = _reflection.GeneratedProtocolMessageType('StringStatistics', (_message.Message,), {
  
    'FreqAndValue' : _reflection.GeneratedProtocolMessageType('FreqAndValue', (_message.Message,), {
      'DESCRIPTOR' : _STRINGSTATISTICS_FREQANDVALUE,
      '__module__' : 'facet_feature_statistics_pb2'
      # @@protoc_insertion_point(class_scope:facetFeatureStatistics.StringStatistics.FreqAndValue)
      })
    ,
    'DESCRIPTOR' : _STRINGSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.StringStatistics)
    })
  _sym_db.RegisterMessage(StringStatistics)
  _sym_db.RegisterMessage(StringStatistics.FreqAndValue)
  
  WeightedNumericStatistics = _reflection.GeneratedProtocolMessageType('WeightedNumericStatistics', (_message.Message,), {
    'DESCRIPTOR' : _WEIGHTEDNUMERICSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.WeightedNumericStatistics)
    })
  _sym_db.RegisterMessage(WeightedNumericStatistics)
  
  WeightedStringStatistics = _reflection.GeneratedProtocolMessageType('WeightedStringStatistics', (_message.Message,), {
    'DESCRIPTOR' : _WEIGHTEDSTRINGSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.WeightedStringStatistics)
    })
  _sym_db.RegisterMessage(WeightedStringStatistics)
  
  BytesStatistics = _reflection.GeneratedProtocolMessageType('BytesStatistics', (_message.Message,), {
    'DESCRIPTOR' : _BYTESSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.BytesStatistics)
    })
  _sym_db.RegisterMessage(BytesStatistics)
  
  StructStatistics = _reflection.GeneratedProtocolMessageType('StructStatistics', (_message.Message,), {
    'DESCRIPTOR' : _STRUCTSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.StructStatistics)
    })
  _sym_db.RegisterMessage(StructStatistics)
  
  CommonStatistics = _reflection.GeneratedProtocolMessageType('CommonStatistics', (_message.Message,), {
    'DESCRIPTOR' : _COMMONSTATISTICS,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.CommonStatistics)
    })
  _sym_db.RegisterMessage(CommonStatistics)
  
  Histogram = _reflection.GeneratedProtocolMessageType('Histogram', (_message.Message,), {
  
    'Bucket' : _reflection.GeneratedProtocolMessageType('Bucket', (_message.Message,), {
      'DESCRIPTOR' : _HISTOGRAM_BUCKET,
      '__module__' : 'facet_feature_statistics_pb2'
      # @@protoc_insertion_point(class_scope:facetFeatureStatistics.Histogram.Bucket)
      })
    ,
    'DESCRIPTOR' : _HISTOGRAM,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.Histogram)
    })
  _sym_db.RegisterMessage(Histogram)
  _sym_db.RegisterMessage(Histogram.Bucket)
  
  RankHistogram = _reflection.GeneratedProtocolMessageType('RankHistogram', (_message.Message,), {
  
    'Bucket' : _reflection.GeneratedProtocolMessageType('Bucket', (_message.Message,), {
      'DESCRIPTOR' : _RANKHISTOGRAM_BUCKET,
      '__module__' : 'facet_feature_statistics_pb2'
      # @@protoc_insertion_point(class_scope:facetFeatureStatistics.RankHistogram.Bucket)
      })
    ,
    'DESCRIPTOR' : _RANKHISTOGRAM,
    '__module__' : 'facet_feature_statistics_pb2'
    # @@protoc_insertion_point(class_scope:facetFeatureStatistics.RankHistogram)
    })
  _sym_db.RegisterMessage(RankHistogram)
  _sym_db.RegisterMessage(RankHistogram.Bucket)
  
  if _descriptor._USE_C_DESCRIPTORS == False:
  
    DESCRIPTOR._options = None
    _STRINGSTATISTICS_FREQANDVALUE.fields_by_name['deprecated_freq']._options = None
    _STRINGSTATISTICS_FREQANDVALUE.fields_by_name['deprecated_freq']._serialized_options = b'\030\001'
    _HISTOGRAM_BUCKET.fields_by_name['deprecated_count']._options = None
    _HISTOGRAM_BUCKET.fields_by_name['deprecated_count']._serialized_options = b'\030\001'
    _RANKHISTOGRAM_BUCKET.fields_by_name['deprecated_count']._options = None
    _RANKHISTOGRAM_BUCKET.fields_by_name['deprecated_count']._serialized_options = b'\030\001'
    _DATASETFEATURESTATISTICSLIST._serialized_start=58
    _DATASETFEATURESTATISTICSLIST._serialized_end=156
    _PATH._serialized_start=158
    _PATH._serialized_end=178
    _DATASETFEATURESTATISTICS._serialized_start=181
    _DATASETFEATURESTATISTICS._serialized_end=339
    _FEATURENAMESTATISTICS._serialized_start=342
    _FEATURENAMESTATISTICS._serialized_end=900
    _FEATURENAMESTATISTICS_TYPE._serialized_start=818
    _FEATURENAMESTATISTICS_TYPE._serialized_end=879
    _WEIGHTEDCOMMONSTATISTICS._serialized_start=902
    _WEIGHTEDCOMMONSTATISTICS._serialized_end=1022
    _CUSTOMSTATISTIC._serialized_start=1025
    _CUSTOMSTATISTIC._serialized_end=1220
    _NUMERICSTATISTICS._serialized_start=1223
    _NUMERICSTATISTICS._serialized_end=1536
    _STRINGSTATISTICS._serialized_start=1539
    _STRINGSTATISTICS._serialized_end=1955
    _STRINGSTATISTICS_FREQANDVALUE._serialized_start=1878
    _STRINGSTATISTICS_FREQANDVALUE._serialized_end=1955
    _WEIGHTEDNUMERICSTATISTICS._serialized_start=1958
    _WEIGHTEDNUMERICSTATISTICS._serialized_end=2087
    _WEIGHTEDSTRINGSTATISTICS._serialized_start=2090
    _WEIGHTEDSTRINGSTATISTICS._serialized_end=2254
    _BYTESSTATISTICS._serialized_start=2257
    _BYTESSTATISTICS._serialized_end=2429
    _STRUCTSTATISTICS._serialized_start=2431
    _STRUCTSTATISTICS._serialized_end=2513
    _COMMONSTATISTICS._serialized_start=2516
    _COMMONSTATISTICS._serialized_end=2908
    _HISTOGRAM._serialized_start=2911
    _HISTOGRAM._serialized_end=3245
    _HISTOGRAM_BUCKET._serialized_start=3100
    _HISTOGRAM_BUCKET._serialized_end=3199
    _HISTOGRAM_HISTOGRAMTYPE._serialized_start=3201
    _HISTOGRAM_HISTOGRAMTYPE._serialized_end=3245
    _RANKHISTOGRAM._serialized_start=3248
    _RANKHISTOGRAM._serialized_end=3454
    _RANKHISTOGRAM_BUCKET._serialized_start=3342
    _RANKHISTOGRAM_BUCKET._serialized_end=3454
  # @@protoc_insertion_point(module_scope)
  
