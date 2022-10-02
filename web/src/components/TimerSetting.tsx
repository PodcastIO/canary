import { InfoCircleOutlined } from '@ant-design/icons';
import { useIntl } from '@umijs/max';
import { DatePicker, Form, InputNumber, Select, Space } from 'antd';

import moment from 'moment';

const { Option } = Select;

export const TimerSetting = () => {
  const intl = useIntl();

  return (
    <>
      <Form.Item
        name="firstExecuteTime"
        label={intl.formatMessage({
          id: 'pages.podcastForm.pullFirstTime',
          defaultMessage: 'First pull time',
        })}
        rules={[
          {
            required: false,
            message: 'Please set first time',
          },
        ]}
        tooltip={{ title: 'first time to get resource', icon: <InfoCircleOutlined /> }}
      >
        <DatePicker
          size="large"
          placeholder="input begin date"
          showTime={true}
          defaultValue={moment()}
        />
      </Form.Item>

      <Form.Item
        label={intl.formatMessage({
          id: 'pages.podcastForm.frequency',
          defaultMessage: 'Frequency',
        })}
        rules={[
          {
            required: true,
            message: 'Please select frequency value',
          },
        ]}
        tooltip={{ title: 'get resource frequencey', icon: <InfoCircleOutlined /> }}
      >
        <Space size="small">
          <Form.Item name="frequencyValue">
            <InputNumber min={1} max={10} defaultValue={1} value={1} />
          </Form.Item>
          <Form.Item name="frequency">
            <Select value={'Hour'} style={{ width: 90 }} defaultValue={'Hour'}>
              <Option value="Hour">
                {intl.formatMessage({
                  id: 'pages.podcastForm.frequency.hour',
                  defaultMessage: 'Hour',
                })}
              </Option>
              <Option value="Day">
                {intl.formatMessage({
                  id: 'pages.podcastForm.frequency.day',
                  defaultMessage: 'Day',
                })}
              </Option>
              <Option value="Week">
                {intl.formatMessage({
                  id: 'pages.podcastForm.frequency.week',
                  defaultMessage: 'Week',
                })}
              </Option>
              <Option value="Month">
                {intl.formatMessage({
                  id: 'pages.podcastForm.frequency.month',
                  defaultMessage: 'Month',
                })}
              </Option>
            </Select>
          </Form.Item>
        </Space>
      </Form.Item>
    </>
  );
};

export default TimerSetting;
