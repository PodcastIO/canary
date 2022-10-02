import { message as toast } from 'antd';
import type { RequestOptionsInit } from 'umi-request';
import { extend } from 'umi-request';

const errorHandler = (error: { response: Response }) => {
  const { response } = error;
  const { status, statusText } = response ?? {};
  try {
    if (status < 200 || status >= 300) {
      response.json().then((res) => {
        const msg = res?.msg || statusText;
        toast.error({ content: msg });
      });
    } else {
      toast.error({ content: 'network appears exception.' });
    }
  } finally {
    throw response;
  }
};

const request = extend({
  errorHandler, // 默认错误处理
  credentials: 'include', // 默认请求是否带上cookie
});

export const getUserToken = (): string => {
  let userToken: string = '';
  if (localStorage.getItem('canary_token')) {
    userToken = localStorage.getItem('canary_token') || '';
  } else {
    userToken = sessionStorage.getItem('canary_token') || '';
  }
  return userToken;
};

export const setUserToken = (token: string) => {
  localStorage.setItem('canary_token', token);
};

request.interceptors.request.use((url: string, options: RequestOptionsInit) => {
  const notCarryTokenArr: string[] = [];
  if (notCarryTokenArr.includes(url)) {
    return {
      url,
      options,
    };
  }
  const headers = {
    Authorization: `Bears ${getUserToken()}`,
    'Content-Type': 'application/json',
  };

  return {
    url,
    options: { ...options, interceptors: true, headers },
  };
});

export const get = async (url: string, parameter?: any): Promise<any> => {
  try {
    const res = await request(url, { method: 'get', ...parameter });
    return res;
  } catch (error) {
    throw error;
  }
};

export const deletes = async (url: string, parameter?: Record<string, unknown>): Promise<any> => {
  try {
    const res = await request(url, { method: 'delete', ...parameter });
    return res;
  } catch (error) {
    throw error;
  }
};

/*post 与 put请求的参数格式：
{
  data:传往后端的参数，
  requestType: 'form' 控制 'Content-Type': 'application/x-www-form-urlencoded; 为这个
}
*/
export const post = async (url: string, args: RequestOptionsInit): Promise<any> => {
  try {
    const res = await request(url, {
      method: 'post',
      ...args,
    });
    return res;
  } catch (error) {
    throw error;
  }
};

export const put = async (url: string, args: RequestOptionsInit): Promise<any> => {
  try {
    const res = await request(url, { method: 'put', ...args });
    return res;
  } catch (error) {
    throw error;
  }
};

export const patch = async (url: string, args: RequestOptionsInit): Promise<any> => {
  try {
    const res = await request(url, { method: 'patch', ...args });
    return res;
  } catch (error) {
    throw error;
  }
};
