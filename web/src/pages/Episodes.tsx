import { ContainerLayout } from '@/components/ContainLayout';
import { get } from '@/services/request';
import { useIntl } from '@umijs/max';
import { Avatar, Button, Layout, List, PageHeader, Skeleton } from 'antd';
import React, { useEffect, useState } from 'react';
import ReactAudioPlayer from 'react-audio-player';

const { Content } = Layout;

const Episodes: React.FC = () => {
  const [initLoading, setInitLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<API.EpisodeItem[]>([]);
  const [list, setList] = useState<API.EpisodeItem[]>([]);
  const [podcasts, setPodcasts] = useState<Map<string, API.PodcastItem>>(
    new Map<string, API.PodcastItem>(),
  );
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  const limit: number = 10;

  const intl = useIntl();

  const setPodcastMap = (partialPodcasts: API.PodcastItem[]) => {
    const newPodcastMap = podcasts;
    partialPodcasts.forEach((item) => {
      newPodcastMap?.set(item.id, item);
    });

    setPodcasts(newPodcastMap);
  };

  useEffect(() => {
    get(`/api/web/episodes?offset=${offset}&limit=${limit}`).then((res) => {
      setPodcastMap(res?.data?.podcasts || []);
      setInitLoading(false);
      setData(res?.data?.episodes || []);
      setList(res?.data?.episodes || []);
      setOffset(offset + res?.data?.episodes.length);
      setTotal(res?.data?.total);
    });
  }, []);

  const onLoadMore = () => {
    setLoading(true);
    setList(
      data.concat(
        [...new Array(3)].map(() => ({
          id: '',
          podcastGid: '',
          title: '',
          description: '',
          content: '',
          link: '',
          coverResourceId: '',
          voiceResourceId: '',
          createdAt: 0,
          pubTime: 0,
        })),
      ),
    );
    get(`/api/web/episodes?offset=${offset}&limit=${limit}`).then((res) => {
      setPodcastMap(res?.data?.podcasts || []);
      const newData = data.concat(res.data.episodes);
      setData(newData);
      setList(newData);
      setLoading(false);
      setTotal(res.data.total);
      setOffset(offset + res.data.episodes.length);
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

  return (
    <ContainerLayout>
      <Content>
        <PageHeader>
          <List
            className="demo-loadmore-list"
            loading={initLoading}
            itemLayout="horizontal"
            loadMore={loadMore}
            dataSource={list}
            renderItem={(item) => {
              const podcast = podcasts?.get(item.podcastGid);
              return (
                <List.Item
                  extra={
                    item.voiceResourceId && (
                      <ReactAudioPlayer
                        src={`/api/web/resource/$${item.voiceResourceId}`}
                        controls
                      />
                    )
                  }
                >
                  <Skeleton avatar title={false} loading={false} active>
                    <List.Item.Meta
                      avatar={
                        <Avatar
                          src={`/api/web/resource/$${
                            item?.coverResourceId ? item?.coverResourceId : podcast?.coverResourceId
                          }`}
                          size={64}
                          shape="square"
                        />
                      }
                      title={<a href={item.link}>{item.title}</a>}
                      description={
                        item.description && item.description !== 'None' ? item.description : ''
                      }
                    />
                  </Skeleton>
                </List.Item>
              );
            }}
          />
        </PageHeader>
      </Content>
    </ContainerLayout>
  );
};

export default Episodes;
