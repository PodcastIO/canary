/** 获取当前的用户 GET /api/currentUser */

import { get, post } from './request';

export async function getUser(): Promise<API.GetUserResponse> {
  return await get('/api/web/user', {});
}

export async function login(params: API.LoginParams): Promise<API.LoginResponse> {
  return await post('/api/web/user/login', { data: params });
}
