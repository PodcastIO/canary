import { get } from '@/services/request';
import { Upload, type UploadFile } from 'antd';
import { useEffect, useState } from 'react';

type CoverFileUploadProps = {
  name: string;
  multiple: boolean;
  accept: string;
  action: string;
  value?: string;
  onChange?: (resourceId: string) => void;
};

export const CoverUpload: React.FC<CoverFileUploadProps> = (props: CoverFileUploadProps) => {
  const [fileList, setFileList] = useState<UploadFile<any>[]>([]);
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
    console.log(info.file.status);
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

  const onPreview = async (file: any) => {
    let src = file.url;

    if (!src) {
      src = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.readAsDataURL(file.originFileObj);

        reader.onload = () => resolve(reader.result);
      });
    }

    const image = new Image();
    image.src = src;
    const imgWindow = window.open(src);
    imgWindow?.document.write(image.outerHTML);
  };

  return (
    <Upload
      action={props.action}
      listType="picture-card"
      maxCount={1}
      fileList={fileList}
      onChange={onChange}
      onPreview={onPreview}
      onRemove={onRemove}
    >
      {fileList.length < 5 && '+ Upload'}
    </Upload>
  );
};
