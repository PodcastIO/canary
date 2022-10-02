import { ContainerLayout } from '@/components/ContainLayout';
import { EditPodcastForm } from '@/components/EditPodcastForm';
import { get } from '@/services/request';
import { FormOutlined, HomeOutlined, LinkOutlined } from '@ant-design/icons';
import { history } from '@umijs/max';
import {
  Avatar,
  Button,
  Col,
  Image,
  Layout,
  List,
  message,
  PageHeader,
  Row,
  Skeleton,
  Space,
  Tooltip,
} from 'antd';
import moment from 'moment';
import React, { useEffect, useState } from 'react';

import ReactAudioPlayer from 'react-audio-player';

import { useLocation } from 'umi';

const { Content } = Layout;

const Podcast: React.FC = () => {
  const [initLoading, setInitLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [podcast, setPodcast] = useState<API.PodcastItem>();
  const [data, setData] = useState<API.EpisodeItem[]>([]);
  const [list, setList] = useState<API.EpisodeItem[]>([]);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);
  const location = useLocation();
  const [editVisible, setEditVisible] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');

  const limit: number = 10;

  const getParam = (key: string): string => {
    const query = new URLSearchParams(location.search);
    const value = query.get(key);
    if (typeof value === 'string') {
      return value;
    }
    return '';
  };
  const id = getParam('id');

  useEffect(() => {
    get(`/api/web/podcast/${id}`).then((res) => {
      setPodcast(res?.data);
    });

    get(`/api/web/podcast/$${id}/episodes?offset=${offset}&limit=${limit}`).then((res) => {
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
    get(`/api/web/podcast/$${id}/episodes?offset=${offset}&limit=${limit}`).then((res) => {
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
        <Button onClick={onLoadMore}>loading more</Button>
      </div>
    ) : null;

  const clipRSSUrl = () => {
    navigator.clipboard.writeText(
      `http://${window.location.host}/api/web/podcast/rss/${podcast?.shareToken}`,
    );
    message.success('Copy RSS URL successfully.');
  };
  return (
    <ContainerLayout>
      <Content>
        {podcast && (
          <PageHeader onBack={() => history.push('/podcasts')} title={podcast?.title}>
            <EditPodcastForm
              visible={editVisible}
              podcastId={podcast.id}
              onClose={() => {
                setEditVisible(false);
              }}
            />

            <Row>
              <Col span={8} />
              <Col
                span={8}
                style={{
                  display: 'inline-flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <Avatar
                  src={<Image src={`/api/web/resource/$${podcast?.coverResourceId}`} />}
                  size={128}
                  shape="square"
                />
              </Col>
              <Col span={8} />
            </Row>
            <Row>
              <Col span={8} />
              <Col
                span={8}
                style={{
                  display: 'inline-flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <Space>
                  <Button
                    shape="circle"
                    icon={<HomeOutlined />}
                    onClick={() => {
                      history.push(podcast?.url);
                    }}
                  />
                  <Tooltip title={copyStatus} trigger={'click|hover'}>
                    <Button
                      shape="circle"
                      icon={<LinkOutlined />}
                      onClick={clipRSSUrl}
                      onMouseEnter={() => {
                        setCopyStatus('Click to copy shared rss URL.');
                      }}
                      disabled={!podcast.shareEnable}
                    />
                  </Tooltip>
                  <Button
                    shape="circle"
                    icon={<FormOutlined />}
                    onClick={() => {
                      setEditVisible(true);
                    }}
                  />
                </Space>
              </Col>
              <Col span={8} />
            </Row>
            <List
              className="demo-loadmore-list"
              loading={initLoading}
              itemLayout="horizontal"
              loadMore={loadMore}
              dataSource={list}
              renderItem={(item) => (
                <List.Item
                  extra={
                    item?.voiceResourceId && (
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
                        item?.coverResourceId && (
                          <Avatar
                            src={`/api/web/resource/$${item?.coverResourceId}`}
                            size={64}
                            shape="square"
                          />
                        )
                      }
                      title={<a href={item.link}>{item.title}</a>}
                      description={moment
                        .unix(item.pubTime ? item.pubTime : item.createdAt)
                        .format('YYYY-MM-DD HH:MM:SS')}
                    />
                  </Skeleton>
                </List.Item>
              )}
            />
          </PageHeader>
        )}
      </Content>
    </ContainerLayout>
  );
};

export default Podcast;
