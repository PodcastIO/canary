import { InfoCircleOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { DatePicker, Form, Switch } from 'antd';
import moment from 'moment';
import { useState } from 'react';

export const ShareSetting = () => {
  const intl = useIntl();
  const [shareEnable, setShareEnable] = useState<boolean>(true);

  const handleShareEnable = (checked: boolean) => {
    setShareEnable(checked);
  };

  return (
    <>
      <Form.Item
        name="shareEnable"
        label={intl.formatMessage({
          id: 'pages.podcastForm.shareEnable',
          defaultMessage: 'Share',
        })}
        tooltip={{ title: 'Enable rss shared or not', icon: <InfoCircleOutlined /> }}
      >
        <Switch onChange={handleShareEnable} />
      </Form.Item>
      {shareEnable && (
        <Form.Item
          name="shareTime"
          label={intl.formatMessage({
            id: 'pages.podcastForm.shareTime',
            defaultMessage: 'Expired time',
          })}
          tooltip={{ title: 'Share expired time', icon: <InfoCircleOutlined /> }}
        >
          <DatePicker
            size="large"
            placeholder="input expire time"
            showTime={true}
            defaultValue={moment()}
          />
        </Form.Item>
      )}
    </>
  );
};

export default ShareSetting;
