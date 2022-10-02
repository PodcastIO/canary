import { GridContent } from '@ant-design/pro-layout';
import { FormattedMessage, useIntl } from '@umijs/max';
import { Card, Result } from 'antd';

const ConfirmLogin: React.FC = () => {
  const intl = useIntl();

  const urlParams = new URL(window.location.href).searchParams;
  const email = urlParams.get('email') || '';
  const emailDomain = email.substring(email.lastIndexOf('@') + 1);

  const title = intl.formatMessage({
    id: 'pages.sendConfirmLogin.title',
    defaultMessage: 'Send login-confirmed email successfully.',
  });

  const subTitle = (
    <FormattedMessage
      id="pages.sendConfirmLogin.subTitle"
      values={{ a: (chunks: any) => <a href={`http://${emailDomain}`}>{chunks}</a> }}
    />
  );
  return (
    <GridContent>
      <Card bordered={false}>
        <Result status="success" title={title} subTitle={subTitle} style={{ marginBottom: 16 }} />
      </Card>
    </GridContent>
  );
};

export default ConfirmLogin;
