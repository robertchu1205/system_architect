cd ${IMAGE_FOLDER_PATH}

wget \
    --user="${USER}" \
    --password="${PASSWORD}" \
    --cut-dirs=1 \
    -m -nH -nv \
    ftp://${FTP}/"${SOURCE_DIR}"