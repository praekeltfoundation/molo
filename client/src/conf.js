import cookies from 'js-cookie';
import { ensure } from 'src/utils';


const conf = {
  apiPrefix: '',
  apiHeaders: {},
  csrfToken: typeof window !== 'undefined'
    ? ensure(cookies.get('csrftoken'), null)
    : null
};


export default conf;
