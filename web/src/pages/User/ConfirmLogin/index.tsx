import { get, setUserToken } from '@/services/request';
import { GridContent } from '@ant-design/pro-layout';
import { FormattedMessage, history, useIntl, useModel } from '@umijs/max';
import { Button, Card, Result } from 'antd';
import { useEffect, useState } from 'react';

const ConfirmLogin: React.FC = () => {
  const intl = useIntl();

  const urlParams = new URL(window.location.href).searchParams;
  const token = urlParams.get('token') || '';
  const userId = urlParams.get('user_id') || '';
  const isRemember = urlParams.get('is_remember') === 'true' ? true : false;

  const [loadStatus, setLoadStatus] = useState<string>('loading');

  const { initialState, setInitialState } = useModel('@@initialState');

  const fetchUserInfo = async () => {
    const userInfo = await initialState?.fetchUserInfo?.();
    if (userInfo) {
      await setInitialState((s) => ({
        ...s,
        currentUser: userInfo,
      }));
    }
  };

  useEffect(() => {
    get(`/api/web/user/confirm_login?token=${token}&user_id=${userId}&is_remember=${isRemember}`)
      .then((resp) => {
        setUserToken(resp?.data?.token);
        fetchUserInfo()
          .then(() => {
            history.push('/');
          })
          .catch((error) => {
            console.log(error);
            setLoadStatus('failed');
          });
      })
      .catch((error) => {
        console.log(error);
        setLoadStatus('failed');
      });
  });
  const title = intl.formatMessage({
    id: 'pages.confirmLogin.title',
    defaultMessage: 'Confirm login failed',
  });

  const backLogin = intl.formatMessage({
    id: 'pages.confirmLogin.backLogin',
    defaultMessage: 'Back to login',
  });

  const subTitle = (
    <FormattedMessage
      id="pages.confirmLogin.subTitle"
      values={{ a: (chunks: any) => <a href={`/user/login`}>{chunks}</a> }}
    />
  );

  const handleBackLogin = () => {
    history.push('/user/login');
  };
  return (
    loadStatus === 'failed' && (
      <GridContent>
        <Card bordered={false}>
          <Result
            status="error"
            title={title}
            subTitle={subTitle}
            extra={
              <Button type="primary" onClick={handleBackLogin}>
                <span>{backLogin}</span>
              </Button>
            }
            style={{ marginTop: 48, marginBottom: 16 }}
          />
        </Card>
      </GridContent>
    )
  );
};

export default ConfirmLogin;
