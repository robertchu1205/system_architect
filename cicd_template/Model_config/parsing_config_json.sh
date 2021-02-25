#!/bin/bash
configjson=$1
# LENGTH=`cat $configjson | jq .model_setting | jq length`
LENGTH=`yq r $configjson --length model_setting`
echo "$LENGTH Components in ${configjson}"
VL_ARRAY=`yq r $configjson --printMode v "model_setting.*.version_label"`
MN_ARRAY=`yq r $configjson --printMode v "model_setting.*.model_name"`
JSON_TO_SAVE="model_config_list:{"
# while [ "$LENGTH" -ne 0 ]
# do
  # LOCATION=`expr $LENGTH - 1`
  # VERSION_LABEL=`cat $configjson | jq -r "[.model_setting[]|.version_label]|.["$LOCATION"]"`
  # MODEL_NAME=`cat $configjson | jq -r "[.model_setting[]|.model_name]|.["$LOCATION"]"`
MODEL_NAME=`echo ${MN_ARRAY} | grep -P '\w+' -o`
VERSION_LABEL=`echo ${VL_ARRAY} | grep -P '\d+' -o`
MODEL_NAME=($(echo $MODEL_NAME | tr " " "\n"))
VERSION_LABEL=($(echo $VERSION_LABEL | tr " " "\n"))
for i in "${!MODEL_NAME[@]}"
do
  echo "$i" "${MODEL_NAME[$i]}" "${VERSION_LABEL[$i]}"
  JSON_STRING="config:{name:'${MODEL_NAME[$i]}',base_path:'/models/${MODEL_NAME[$i]}',model_platform:'tensorflow',model_version_policy:{specific:{versions:${VERSION_LABEL[$i]}}}}"
  JSON_TO_SAVE="${JSON_TO_SAVE}${JSON_STRING}"
done
  # LENGTH=`expr $LENGTH - 1`
# done
echo "$JSON_TO_SAVE}" > $2
exit 0