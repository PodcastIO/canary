import { Layout } from 'antd';

const { Sider } = Layout;

export const ContainerLayout = ({ children }: { children: any }) => {
  return (
    <>
      <Layout>
        <Sider style={{ visibility: 'hidden' }} />
        {children}
        <Sider style={{ visibility: 'hidden' }} />
      </Layout>
    </>
  );
};
