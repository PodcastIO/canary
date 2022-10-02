import { get, put } from '@/services/request';
import { useIntl } from '@umijs/max';
import { Button, Drawer, Form, Input, message, Radio, Select, Space } from 'antd';
import moment from 'moment';
import { useEffect, useRef, useState } from 'react';
import { CoverUpload } from './CoverUpload';
import { FileUpload } from './FileUpload';
import ShareSetting from './ShareSetting';
import TimerSetting from './TimerSetting';

const { Option } = Select;

export const EditPodcastForm = ({
  podcastId,
  visible,
  onClose,
}: {
  podcastId: string;
  visible: boolean;
  onClose: () => void;
}) => {
  const [podcastItem, setPodcastItem] = useState<API.PodcastItem>();
  const [editForm] = Form.useForm();
  const submitBtnRef = useRef<HTMLElement | undefined>();

  const clearForm = () => {
    const tmpPodcastItem = {
      id: '',
      source: '',
      title: '',
      language: '',
      author: '',
      bookResourceId: '',
      coverResourceId: '',
      description: '',
      firstExecuteTime: '',
      frequencyValue: 0,
      frequency: '',
      url: '',
      shareEnable: false,
      shareTime: '',
    };

    setPodcastItem(tmpPodcastItem);
    editForm.setFieldsValue(tmpPodcastItem);
  };

  const intl = useIntl();

  useEffect(() => {
    if (podcastId && podcastId.length > 0) {
      get(`/api/web/podcast/${podcastId}`).then((res: any) => {
        const tmpPodcastItem = {
          id: res?.data?.id,
          source: res?.data?.source,
          title: res?.data?.title,
          language: res?.data?.language,
          author: res?.data?.author,
          bookResourceId: res?.data?.bookResourceId,
          coverResourceId: res?.data?.coverResourceId,
          description: res?.data?.description,
          firstExecuteTime: moment.unix(Number(res?.data?.firstExecuteTime)),
          frequencyValue: res?.data?.frequencyValue,
          frequency: res?.data?.frequency,
          url: res?.data?.url,
          shareEnable: res?.data?.shareEnable === 0 ? false : true,
          shareTime: res?.data?.shareTime ? moment.unix(Number(res?.data?.shareTime)) : moment(),
        };
        setPodcastItem(tmpPodcastItem);
        editForm.setFieldsValue(tmpPodcastItem);
        // Resetting window's offsetTop so as to display react-virtualized demo underfloor.
        // In real scene, you can using public method of react-virtualized:
        // https://stackoverflow.com/questions/46700726/how-to-use-public-method-updateposition-of-react-virtualized
        window.dispatchEvent(new Event('resize'));
      });
    }

    if (!visible) {
      clearForm();
    }
  }, [podcastId]);

  const handleOnClose = () => {
    clearForm();
    onClose();
  };

  const handleOnSubmit = () => {
    if (typeof submitBtnRef.current?.onclick === 'function') {
      submitBtnRef.current?.click();
    }
  };

  const onFinish = (values: any) => {
    console.log('onFinish:', values);
    put(`/api/web/podcast/${podcastId}`, {
      body: JSON.stringify({
        title: values?.title,
        author: values?.author,
        description: values?.description,
        coverResourceId: values?.coverResourceId,
        bookResourceId: values?.bookResourceId,
        frequency: values?.frequency,
        frequencyValue: values?.frequencyValue ? Number(values.frequencyValue) : null,
        firstExecuteTime: values?.firstExecuteTime ? values.firstExecuteTime.unix() : null,
        shareEnable: values?.shareEnable ? 1 : 0,
        shareTime: values?.shareTime ? values.shareTime.unix() : moment().unix(),
      }),
    })
      .then((res: any) => {
        if (res?.code === 0) {
          handleOnClose();
        } else {
          message.error(res.statusText);
        }
      })
      .catch((error) => {
        message.error(error);
      });
  };

  return (
    <>
      {podcastItem && (
        <Drawer
          title={intl.formatMessage({
            id: 'pages.podcastForm.editTitle',
            defaultMessage: 'Edit podcast',
          })}
          width={720}
          onClose={handleOnClose}
          visible={visible}
          bodyStyle={{
            paddingBottom: 80,
          }}
          extra={
            <Space>
              <Button onClick={handleOnClose}>Cancel</Button>
              <Button onClick={handleOnSubmit} type="primary">
                Submit
              </Button>
            </Space>
          }
        >
          <Form
            form={editForm}
            labelCol={{ span: 4 }}
            wrapperCol={{ span: 14 }}
            layout="horizontal"
            onFinish={onFinish}
          >
            <Form.Item
              name="source"
              label={intl.formatMessage({
                id: 'pages.podcastForm.source',
                defaultMessage: 'Source',
              })}
            >
              <Radio.Group
                value={podcastItem.source}
                disabled={true}
                defaultValue={podcastItem.source}
              >
                <Radio value="Local">
                  {intl.formatMessage({
                    id: 'pages.podcastForm.localSource',
                    defaultMessage: 'Local',
                  })}
                </Radio>
                <Radio value="RSS">
                  {intl.formatMessage({
                    id: 'pages.podcastForm.rssSource',
                    defaultMessage: 'RSS',
                  })}
                </Radio>
                <Radio value="Video">
                  {intl.formatMessage({
                    id: 'pages.podcastForm.videoSource',
                    defaultMessage: 'Video',
                  })}
                </Radio>
              </Radio.Group>
            </Form.Item>
            {podcastItem.source === 'Local' && (
              <Form.Item
                name="bookResourceId"
                label={intl.formatMessage({
                  id: 'pages.podcastForm.localFile',
                  defaultMessage: 'Local file',
                })}
                rules={[
                  {
                    required: true,
                    message: intl.formatMessage({
                      id: 'pages.podcastForm.localFile.placeholder',
                      defaultMessage: 'Please uplaod file',
                    }),
                  },
                ]}
              >
                <FileUpload
                  disabled={true}
                  name={'file'}
                  multiple={false}
                  action={'/api/web/resource/book'}
                  accept={'.doc,.docx,.pdf,.epub,.mobi'}
                />
              </Form.Item>
            )}
            {podcastItem.source === 'RSS' && (
              <Form.Item
                label={intl.formatMessage({
                  id: 'pages.podcastForm.rssUrl',
                  defaultMessage: 'RSS URL',
                })}
              >
                <Form.Item name="url">
                  <Input placeholder="Please enter rss url" disabled={true} />
                </Form.Item>
              </Form.Item>
            )}
            {podcastItem.source === 'Video' && (
              <Form.Item
                name="url"
                label={intl.formatMessage({
                  id: 'pages.podcastForm.videoUrl',
                  defaultMessage: 'Video URL',
                })}
                rules={[
                  {
                    required: true,
                    message: 'Please enter video url',
                  },
                ]}
              >
                <Input type="text" disabled={true} />
              </Form.Item>
            )}
            {(podcastItem.source == 'RSS' || podcastItem.source == 'Video') && <TimerSetting />}

            <Form.Item
              name="language"
              label={intl.formatMessage({
                id: 'pages.podcastForm.language',
                defaultMessage: 'Language',
              })}
              rules={[
                {
                  required: true,
                  message: 'Please select language',
                },
              ]}
            >
              <Select
                style={{ width: '100%' }}
                placeholder="select one country"
                optionLabelProp="label"
                disabled={true}
              >
                <Option
                  value="zh"
                  label={intl.formatMessage({
                    id: 'pages.podcastForm.language.chinese',
                    defaultMessage: 'Chinese',
                  })}
                >
                  <div className="demo-option-label-item">
                    <span
                      role="img"
                      aria-label={intl.formatMessage({
                        id: 'pages.podcastForm.language.chinese',
                        defaultMessage: 'Chinese',
                      })}
                    >
                      🇨🇳
                    </span>
                    {intl.formatMessage({
                      id: 'pages.podcastForm.language.chinese',
                      defaultMessage: 'Chinese',
                    })}
                  </div>
                </Option>
                <Option
                  value="en"
                  label={intl.formatMessage({
                    id: 'pages.podcastForm.language.english',
                    defaultMessage: 'English',
                  })}
                >
                  <div className="demo-option-label-item">
                    <span
                      role="img"
                      aria-label={intl.formatMessage({
                        id: 'pages.podcastForm.language.english',
                        defaultMessage: 'English',
                      })}
                    >
                      🇺🇸
                    </span>
                    {intl.formatMessage({
                      id: 'pages.podcastForm.language.english',
                      defaultMessage: 'English',
                    })}
                  </div>
                </Option>
                <Option
                  value="jp"
                  label={intl.formatMessage({
                    id: 'pages.podcastForm.language.japanese',
                    defaultMessage: 'Japanese',
                  })}
                >
                  <div className="demo-option-label-item">
                    <span
                      role="img"
                      aria-label={intl.formatMessage({
                        id: 'pages.podcastForm.language.japanese',
                        defaultMessage: 'Japanese',
                      })}
                    >
                      🇯🇵
                    </span>
                    {intl.formatMessage({
                      id: 'pages.podcastForm.language.japanese',
                      defaultMessage: 'Japanese',
                    })}
                  </div>
                </Option>
                <Option
                  value="ko"
                  label={intl.formatMessage({
                    id: 'pages.podcastForm.language.korea',
                    defaultMessage: 'Korea',
                  })}
                >
                  <div className="demo-option-label-item">
                    <span
                      role="img"
                      aria-label={intl.formatMessage({
                        id: 'pages.podcastForm.language.korea',
                        defaultMessage: 'Korea',
                      })}
                    >
                      🇰🇷
                    </span>
                    {intl.formatMessage({
                      id: 'pages.podcastForm.language.korea',
                      defaultMessage: 'Korea',
                    })}
                  </div>
                </Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="title"
              label={intl.formatMessage({
                id: 'pages.podcastForm.title',
                defaultMessage: 'Title',
              })}
              rules={[
                {
                  required: true,
                  message: intl.formatMessage({
                    id: 'pages.podcastForm.title.placeholder',
                    defaultMessage: 'Please enter title',
                  }),
                },
              ]}
            >
              <Input
                placeholder={intl.formatMessage({
                  id: 'pages.podcastForm.title.placeholder',
                  defaultMessage: 'Please enter title',
                })}
                defaultValue={podcastItem.title}
                value={podcastItem.title}
              />
            </Form.Item>
            <Form.Item
              name="author"
              label={intl.formatMessage({
                id: 'pages.podcastForm.author',
                defaultMessage: 'Author',
              })}
              rules={[
                {
                  required: true,
                  message: intl.formatMessage({
                    id: 'pages.podcastForm.author.placeholder',
                    defaultMessage: 'Please enter author',
                  }),
                },
              ]}
            >
              <Input
                placeholder={intl.formatMessage({
                  id: 'pages.podcastForm.author.placeholder',
                  defaultMessage: 'Please enter author',
                })}
                defaultValue={podcastItem.author}
                value={podcastItem.author}
              />
            </Form.Item>
            <Form.Item
              label={intl.formatMessage({
                id: 'pages.podcastForm.cover',
                defaultMessage: 'Cover',
              })}
            >
              <Form.Item name="coverResourceId">
                <CoverUpload
                  name={'file'}
                  multiple={false}
                  action={'/api/web/resource/cover'}
                  accept={'.jpg,.jpeg,.png'}
                />
              </Form.Item>
            </Form.Item>
            <Form.Item
              name="description"
              label={intl.formatMessage({
                id: 'pages.podcastForm.description',
                defaultMessage: 'Description',
              })}
            >
              <Input.TextArea
                rows={4}
                placeholder={intl.formatMessage({
                  id: 'pages.podcastForm.description.placeholder',
                  defaultMessage: 'Please enter description',
                })}
                value={podcastItem.description}
              />
            </Form.Item>
            <ShareSetting />

            <Form.Item wrapperCol={{ span: 12, offset: 6 }}>
              <Button
                type="primary"
                htmlType="submit"
                ref={submitBtnRef}
                style={{ visibility: 'hidden' }}
              >
                Submit
              </Button>
            </Form.Item>
          </Form>
        </Drawer>
      )}
    </>
  );
};
