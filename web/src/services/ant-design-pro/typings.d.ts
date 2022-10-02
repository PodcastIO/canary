// @ts-ignore
/* eslint-disable */

declare namespace API {
  type HttpResponse<T> = {
    code?: number;
    msg?: string;
    data?: T;
  };

  type CurrentUser = {
    name?: string;
    avatar?: string;
    userid?: string;
    email?: string;
    signature?: string;
    title?: string;
    group?: string;
    tags?: { key?: string; label?: string }[];
    notifyCount?: number;
    unreadCount?: number;
    country?: string;
    access?: string;
    geographic?: {
      province?: { label?: string; key?: string };
      city?: { label?: string; key?: string };
    };
    address?: string;
    phone?: string;
  };

  type GetUserResponse = HttpResponse<CurrentUser>;

  type PageParams = {
    current?: number;
    pageSize?: number;
  };

  type PodcastItem = {
    id: string;
    source: string;
    title: string;
    author: string;
    language: string;
    coverResourceId: string;
    bookResourceId: string;
    description: string;
    firstExecuteTime: moment;
    frequencyValue: number;
    frequency: string;
    url: string;
    shareEnable: boolean;
    shareTime: moment;
    shareToken: string;
  };

  type PodcastItemList = {
    data?: {
      items: PodcastItem[];
      total: number;
    };
    code: number;
    message: string;
  };

  type EpisodeItem = {
    id: string;
    podcastGid: string;
    title: string;
    description: string;
    content: string;
    link: string;
    coverResourceId: string;
    voiceResourceId: string;
    createdAt: number;
    pubTime?: number;
  };

  type EpisodeItemList = {
    data?: {
      items: EpisodeItem[];
      total: number;
    };
    code: number;
    message: string;
  };

  type FakeCaptcha = {
    code?: number;
    status?: string;
  };

  type LoginParams = {
    email?: string;
    isRemember?: boolean;
  };

  type LoginResponse = HttpResponse<null>;

  type ErrorResponse = {
    /** 业务约定的错误码 */
    errorCode: string;
    /** 业务上的错误信息 */
    errorMessage?: string;
    /** 业务上的请求是否成功 */
    success?: boolean;
  };

  type NoticeIconList = {
    data?: NoticeIconItem[];
    /** 列表的内容总数 */
    total?: number;
    success?: boolean;
  };

  type NoticeIconItemType = 'notification' | 'message' | 'event';

  type NoticeIconItem = {
    id?: string;
    extra?: string;
    key?: string;
    read?: boolean;
    avatar?: string;
    title?: string;
    status?: string;
    datetime?: string;
    description?: string;
    type?: NoticeIconItemType;
  };
}
