export default [
  {
    path: '/user',
    layout: false,
    routes: [
      {
        name: 'login',
        path: '/user/login',
        component: './User/Login',
      },
      {
        name: 'sendConfirmLogin',
        path: '/user/sendConfirmLogin',
        component: './User/SendConfirmLogin',
      },
      {
        name: 'confirmLogin',
        path: '/user/confirmLogin',
        component: './User/ConfirmLogin',
      },
      {
        component: './404',
      },
    ],
  },
  {
    path: '/podcast',
    component: './Podcast',
  },
  {
    path: '/podcasts',
    name: 'podcasts',
    component: './Podcasts',
  },
  {
    path: '/episodes',
    name: 'episodes',
    component: './Episodes',
  },
  {
    path: '/',
    redirect: '/podcasts',
  },
  {
    component: './404',
  },
];
