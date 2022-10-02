import { post } from '@/services/request';
import { useIntl } from '@umijs/max';
import { Button, Drawer, Form, Input, message, Radio, Select, Space } from 'antd';
import moment from 'moment';
import { useRef, useState } from 'react';
import { CoverUpload } from './CoverUpload';
import { FileUpload } from './FileUpload';
import ShareSetting from './ShareSetting';
import TimerSetting from './TimerSetting';

const { Option } = Select;

export const CreatePodcastForm: React.FC = (props: any) => {
  const submitBtnRef = useRef<HTMLElement | undefined>();

  const onClose = () => {
    props.onClose();
  };

  const handleOnClose = () => {
    onClose();
  };

  const handleOnSubmit = () => {
    if (typeof submitBtnRef.current?.onclick === 'function') {
      submitBtnRef.current?.click();
    }
  };

  const intl = useIntl();
  const [source, setSource] = useState('Local');
  const [createForm] = Form.useForm();

  const handleChangeSource = (e: any) => {
    setSource(e.target.value);
    if (e.target.value === 'RSS' || e.target.value === 'Video') {
      createForm.setFieldsValue({
        firstExecuteTime: moment(),
        frequencyValue: 1,
        frequency: 'Hour',
      });
    }
  };

  const onFinish = (values: any) => {
    console.log('onFinish:', values);
    post(`/api/web/podcast`, {
      body: JSON.stringify({
        source: source,
        title: values?.title,
        author: values?.author,
        description: values?.description,
        url: values?.url,
        coverResourceId: values?.coverResourceId,
        bookResourceId: values?.bookResourceId,
        language: values?.language,
        frequency: values?.frequency,
        frequencyValue: values?.frequencyValue ? Number(values.frequencyValue) : null,
        firstExecuteTime: values?.firstExecuteTime ? values.firstExecuteTime.unix() : null,
      }),
    })
      .then((res: any) => {
        if (res?.code === 0) {
          handleOnClose();
        } else {
          message.error(res.msg);
        }
      })
      .catch((error) => {
        message.error(error);
      });
  };

  return (
    <>
      <Drawer
        title={intl.formatMessage({
          id: 'pages.podcastForm.addTitle',
          defaultMessage: 'Add podcast',
        })}
        width={720}
        onClose={handleOnClose}
        visible={props.visible}
        bodyStyle={{
          paddingBottom: 80,
        }}
        extra={
          <Space>
            <Button onClick={onClose}>
              {intl.formatMessage({
                id: 'pages.podcastForm.cancel',
                defaultMessage: 'Cancel',
              })}
            </Button>
            <Button onClick={handleOnSubmit} type="primary">
              {intl.formatMessage({
                id: 'pages.podcastForm.submit',
                defaultMessage: 'Submit',
              })}
            </Button>
          </Space>
        }
      >
        <Form
          form={createForm}
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
            <Radio.Group value={source} defaultValue={source} onChange={handleChangeSource}>
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
          {source == 'Local' && (
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
                name={'file'}
                multiple={false}
                action={'/api/web/resource/book'}
                accept={'.doc,.docx,.pdf,.epub,.mobi'}
              />
            </Form.Item>
          )}
          {source == 'RSS' && (
            <Form.Item
              name="url"
              label={intl.formatMessage({
                id: 'pages.podcastForm.rssUrl',
                defaultMessage: 'RSS URL',
              })}
              rules={[
                {
                  required: true,
                  message: intl.formatMessage({
                    id: 'pages.podcastForm.rssUrl.placeholder',
                    defaultMessage: 'Please enter RSS url',
                  }),
                },
              ]}
            >
              <Input
                placeholder={intl.formatMessage({
                  id: 'pages.podcastForm.rssUrl.placeholder',
                  defaultMessage: 'Please enter RSS url',
                })}
              />
            </Form.Item>
          )}
          {source == 'Video' && (
            <Form.Item
              name="url"
              label={intl.formatMessage({
                id: 'pages.podcastForm.videoUrl',
                defaultMessage: 'Video URL',
              })}
              rules={[
                {
                  required: true,
                  message: intl.formatMessage({
                    id: 'pages.podcastForm.videoUrl.placeholder',
                    defaultMessage: 'Please enter video url',
                  }),
                },
              ]}
            >
              <Input
                placeholder={intl.formatMessage({
                  id: 'pages.podcastForm.videoUrl.placeholder',
                  defaultMessage: 'Please enter video url',
                })}
              />
            </Form.Item>
          )}
          {(source == 'RSS' || source == 'Video') && <TimerSetting />}
          <Form.Item
            name="language"
            label={intl.formatMessage({
              id: 'pages.podcastForm.language',
              defaultMessage: 'Language',
            })}
            rules={[
              {
                required: true,
                message: intl.formatMessage({
                  id: 'pages.podcastForm.language.placeholder',
                  defaultMessage: 'Please select language',
                }),
              },
            ]}
          >
            <Select
              style={{ width: '100%' }}
              placeholder="select one country"
              defaultValue={[]}
              optionLabelProp="label"
            >
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
                value="de"
                label={intl.formatMessage({
                  id: 'pages.podcastForm.language.german',
                  defaultMessage: 'German',
                })}
              >
                <div className="demo-option-label-item">
                  <span
                    role="img"
                    aria-label={intl.formatMessage({
                      id: 'pages.podcastForm.language.german',
                      defaultMessage: 'German',
                    })}
                  >
                    🇩🇪
                  </span>
                  {intl.formatMessage({
                    id: 'pages.podcastForm.language.german',
                    defaultMessage: 'German',
                  })}
                </div>
              </Option>
              <Option
                value="ne"
                label={intl.formatMessage({
                  id: 'pages.podcastForm.language.netherlands',
                  defaultMessage: 'Netherlands',
                })}
              >
                <div className="demo-option-label-item">
                  <span
                    role="img"
                    aria-label={intl.formatMessage({
                      id: 'pages.podcastForm.language.netherlands',
                      defaultMessage: 'Netherlands',
                    })}
                  >
                    🇳🇱
                  </span>
                  {intl.formatMessage({
                    id: 'pages.podcastForm.language.netherlands',
                    defaultMessage: 'Netherlands',
                  })}
                </div>
              </Option>
              <Option
                value="fr"
                label={intl.formatMessage({
                  id: 'pages.podcastForm.language.french',
                  defaultMessage: 'French',
                })}
              >
                <div className="demo-option-label-item">
                  <span
                    role="img"
                    aria-label={intl.formatMessage({
                      id: 'pages.podcastForm.language.french',
                      defaultMessage: 'French',
                    })}
                  >
                    🇳🇱
                  </span>
                  {intl.formatMessage({
                    id: 'pages.podcastForm.language.french',
                    defaultMessage: 'French',
                  })}
                </div>
              </Option>
              <Option
                value="es"
                label={intl.formatMessage({
                  id: 'pages.podcastForm.language.spanish',
                  defaultMessage: 'Spanish',
                })}
              >
                <div className="demo-option-label-item">
                  <span
                    role="img"
                    aria-label={intl.formatMessage({
                      id: 'pages.podcastForm.language.spanish',
                      defaultMessage: 'Spanish',
                    })}
                  >
                    🇵🇹
                  </span>
                  {intl.formatMessage({
                    id: 'pages.podcastForm.language.spanish',
                    defaultMessage: 'Spanish',
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
                id: 'pages.podcastForm.language.placeholder',
                defaultMessage: 'Please enter author',
              })}
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
    </>
  );
};
