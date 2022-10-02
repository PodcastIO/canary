import { get } from '@/services/request';
import { InboxOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { Upload, UploadFile } from 'antd';
import React, { useEffect, useState } from 'react';

const { Dragger } = Upload;

type CustomFileUploadProps = {
  name: string;
  accept: string;
  multiple: boolean;
  action: string;
  value?: string;
  disabled?: boolean;
  onChange?: (resourceId: string) => void;
};

export const FileUpload: React.FC<CustomFileUploadProps> = (props: CustomFileUploadProps) => {
  const [fileList, setFileList] = useState<UploadFile<any>[]>([]);
  const intl = useIntl();

  useEffect(() => {
    if (props.value && props.value.length > 0) {
      get(`/api/web/resource/$${props.value}/detail`).then((res) => {
        setFileList([
          {
            uid: res?.data?.id,
            name: res?.data?.name,
            fileName: res?.data?.name,
            status: 'done',
            url: `/api/web/resource/$${props.value}`,
            preview: `/api/web/resource/$${props.value}`,
          },
        ]);
        if (typeof props.onChange === 'function') {
          props.onChange(res?.data?.id);
        }
        // Resetting window's offsetTop so as to display react-virtualized demo underfloor.
        // In real scene, you can using public method of react-virtualized:
        // https://stackoverflow.com/questions/46700726/how-to-use-public-method-updateposition-of-react-virtualized
        window.dispatchEvent(new Event('resize'));
      });
    } else {
      setFileList([]);
    }
  }, [props.value]);

  const onChange = (info: any) => {
    if (info.file.status === 'done') {
      if (typeof props.onChange === 'function') {
        props.onChange(info?.file?.response?.data?.id);
      }
    }
    setFileList(info.fileList);
  };

  const onRemove = (file: UploadFile<any>) => {
    const tmpFileList = fileList.filter(function (obj) {
      return obj.uid !== file.uid;
    });
    setFileList(tmpFileList);
    return true;
  };

  const onDrop = (e: any) => {
    console.log('Dropped files', e.dataTransfer.files);
  };
  return (
    <Dragger
      name={props.name}
      multiple={props.multiple}
      maxCount={1}
      disabled={props.disabled}
      fileList={fileList}
      action={props.action}
      onChange={onChange}
      onRemove={onRemove}
      onDrop={onDrop}
    >
      <p className="ant-upload-drag-icon">
        <InboxOutlined />
      </p>
      <p className="ant-upload-text">
        {intl.formatMessage({
          id: 'pages.uploadFile.description',
          defaultMessage: 'Click or drag file to this area to upload',
        })}
      </p>
    </Dragger>
  );
};
