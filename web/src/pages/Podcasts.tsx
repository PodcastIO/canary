import { ContainerLayout } from '@/components/ContainLayout';
import { CreatePodcastForm } from '@/components/CreatePodcastForm';
import { EditPodcastForm } from '@/components/EditPodcastForm';
import { deletes, get } from '@/services/request';
import { FormattedMessage, useIntl } from '@umijs/max';
import { Avatar, Button, Layout, List, PageHeader, Skeleton } from 'antd';
import moment from 'moment';
import React, { useEffect, useState } from 'react';

const { Content } = Layout;

const Podcasts: React.FC = () => {
  const [initLoading, setInitLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<API.PodcastItem[]>([]);
  const [list, setList] = useState<API.PodcastItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [visible, setVisible] = useState(false);
  const [editVisible, setEditVisible] = useState(false);
  const [editPodcastId, setEditPodcastId] = useState('');
  const [total, setTotal] = useState(0);

  const limit: number = 10;

  const intl = useIntl();

  useEffect(() => {
    get(`/api/web/podcasts?offset=${offset}&limit=${limit}`).then((res) => {
      setInitLoading(false);
      setData(res?.data?.items || []);
      setList(res?.data?.items || []);
      setOffset(offset + res?.data?.items.length);
      setTotal(res?.data?.total);
    });
  }, []);

  const onLoadMore = () => {
    setLoading(true);
    setList(
      data.concat(
        [...new Array(limit)].map(() => ({
          id: '',
          source: '',
          title: '',
          author: '',
          language: '',
          coverResourceId: '',
          bookResourceId: '',
          description: '',
          firstExecuteTime: moment(),
          frequencyValue: 0,
          frequency: '',
          url: '',
          shareEnable: false,
          shareTime: 0,
          shareToken: '',
        })),
      ),
    );
    get(`/api/web/podcasts?offset=${offset}&limit=${limit}`).then((res) => {
      const newData = data.concat(res.data.items);
      setData(newData);
      setList(newData);
      setLoading(false);
      setTotal(res.data.total);
      setOffset(offset + res.data.items.length);
      // Resetting window's offsetTop so as to display react-virtualized demo underfloor.
      // In real scene, you can using public method of react-virtualized:
      // https://stackoverflow.com/questions/46700726/how-to-use-public-method-updateposition-of-react-virtualized
      window.dispatchEvent(new Event('resize'));
    });
  };

  const loadMore =
    !initLoading && !loading && list.length >= 0 && list.length < total ? (
      <div
        style={{
          textAlign: 'center',
          marginTop: 12,
          height: 32,
          lineHeight: '32px',
        }}
      >
        <Button onClick={onLoadMore}>
          {intl.formatMessage({ id: 'pages.podcasts.loadingMore', defaultMessage: 'loading more' })}
        </Button>
      </div>
    ) : null;

  const handleRemove = (podcastId: string) => {
    deletes(`/api/web/podcast/$${podcastId}`).then(() => {
      const tmp = list.filter((item) => item.id !== podcastId);
      setList(tmp);
    });
  };
  return (
    <ContainerLayout>
      <Content>
        <CreatePodcastForm
          visible={visible}
          onClose={() => {
            setVisible(false);
          }}
        />
        <EditPodcastForm
          visible={editVisible}
          podcastId={editPodcastId}
          onClose={() => {
            setEditVisible(false);
            setEditPodcastId('');
          }}
        />
        <PageHeader
          extra={[
            <Button
              key="1"
              type="primary"
              onClick={() => {
                setVisible(true);
              }}
            >
              {intl.formatMessage({
                id: 'pages.podcasts.addPodcastBtn.title',
                defaultMessage: 'Add Podcast',
              })}
            </Button>,
          ]}
        >
          <List
            className="demo-loadmore-list"
            loading={initLoading}
            itemLayout="horizontal"
            loadMore={loadMore}
            dataSource={list}
            renderItem={(item) => (
              <List.Item
                actions={[
                  <a
                    key="list-loadmore-edit"
                    onClick={() => {
                      setEditPodcastId(item.id);
                      setEditVisible(true);
                    }}
                  >
                    <FormattedMessage id="pages.podcasts.edit" defaultMessage="Edit" />
                  </a>,
                  <a
                    key="list-loadmore-remove"
                    style={{ color: '#ff5655' }}
                    onClick={() => {
                      handleRemove(item.id);
                    }}
                  >
                    <FormattedMessage id="pages.podcasts.remove" defaultMessage="Remove" />
                  </a>,
                ]}
              >
                <Skeleton avatar title={false} loading={false} active>
                  <List.Item.Meta
                    avatar={
                      <Avatar
                        src={`/api/web/resource/$${item.coverResourceId}`}
                        size={64}
                        shape="square"
                      />
                    }
                    title={<a href={`/podcast?id=${item.id}&title=${item.title}`}>{item.title}</a>}
                    description={
                      item.description && item.description !== 'None' ? item.description : ''
                    }
                  />
                </Skeleton>
              </List.Item>
            )}
          />
        </PageHeader>
      </Content>
    </ContainerLayout>
  );
};

export default Podcasts;
