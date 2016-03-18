import cookies from 'cookies-js';
import { ensure } from 'src/utils';


const conf = {
  apiPrefix: '',
  csrfToken: typeof window !== 'undefined'
    ? ensure(cookies(window).get('csrftoken'), null)
    : null
};


export default conf;
