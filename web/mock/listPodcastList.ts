import { Request, Response } from 'express';

// mock tableListDataSource
const genList = (current: number, offset: number) => {
  const tableListDataSource: API.PodcastItem[] = [];

  for (let i = 0; i < offset; i += 1) {
    const index = (current - 1) * 10 + i;
    tableListDataSource.push({
      id: index.toString(10),
      title: `Podcast ${index}`,
      author: '阮一峰',
      cover_resource_id: '1234143',
      description: '阮一峰日志播客12341234124124',
      url: 'https://www.ruanyifeng.com',
    });
  }
  tableListDataSource.reverse();
  return tableListDataSource;
};

let tableListDataSource = genList(1, 100);

function getPodcasts(req: Request, res: Response, u: string) {
  console.log(u);
  let realUrl = u;
  if (!realUrl || Object.prototype.toString.call(realUrl) !== '[object String]') {
    realUrl = req.url;
  }
  let { offset = 1, limit = 10 } = req.query;
  let data: API.PodcastItem[] = [];
  if (tableListDataSource.length > offset) {
    data = tableListDataSource.slice(Number(offset), Number(offset) + Number(limit));
  } else {
    data = [];
  }

  const result = {
    data: {
      items: data,
      total: tableListDataSource.length,
    },
    code: 0,
    message: 'succes',
    offset: offset,
    limit: limit,
  };

  return res.json(result);
}

export default {
  'GET /api/web/podcasts': getPodcasts,
};
