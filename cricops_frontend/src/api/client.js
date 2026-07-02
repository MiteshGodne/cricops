import axios from 'axios';

const store = window.sessionStorage;

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
});

client.interceptors.request.use((config) => {
  const token = store.getItem('access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let queue = [];
const processQueue = (token) => { queue.forEach((cb) => cb(token)); queue = []; };

client.interceptors.response.use(
  (res) => res,
  async (error) => {
    const orig = error.config;
    if (error.response?.status === 401 && !orig._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          queue.push((token) => {
            orig.headers.Authorization = `Bearer ${token}`;
            resolve(client(orig));
          });
        });
      }
      orig._retry = true;
      isRefreshing = true;
      try {
        const refresh = store.getItem('refresh');
        if (!refresh) throw new Error('No refresh token');
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_BASE_URL}/accounts/token/refresh/`,
          { refresh }
        );
        store.setItem('access', data.access);
        processQueue(data.access);
        orig.headers.Authorization = `Bearer ${data.access}`;
        return client(orig);
      } catch {
        store.removeItem('access');
        store.removeItem('refresh');
        window.location.href = '/login';
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export { store };
export default client;


// import axios from 'axios';

// const client = axios.create({
//   baseURL: import.meta.env.VITE_API_BASE_URL,
//   timeout: 15000,
// });

// client.interceptors.request.use((config) => {
//   const token = localStorage.getItem('access');
//   if (token) config.headers.Authorization = `Bearer ${token}`;
//   return config;
// });

// let isRefreshing = false;
// let queue = [];

// const processQueue = (token) => {
//   queue.forEach((cb) => cb(token));
//   queue = [];
// };

// client.interceptors.response.use(
//   (res) => res,
//   async (error) => {
//     const originalRequest = error.config;
//     if (error.response?.status === 401 && !originalRequest._retry) {
//       if (isRefreshing) {
//         return new Promise((resolve) => {
//           queue.push((token) => {
//             originalRequest.headers.Authorization = `Bearer ${token}`;
//             resolve(client(originalRequest));
//           });
//         });
//       }
//       originalRequest._retry = true;
//       isRefreshing = true;
//       try {
//         const refresh = localStorage.getItem('refresh');
//         const { data } = await axios.post(
//           `${import.meta.env.VITE_API_BASE_URL}/accounts/token/refresh/`,
//           { refresh }
//         );
//         localStorage.setItem('access', data.access);
//         processQueue(data.access);
//         originalRequest.headers.Authorization = `Bearer ${data.access}`;
//         return client(originalRequest);
//       } catch (err) {
//         localStorage.removeItem('access');
//         localStorage.removeItem('refresh');
//         window.location.href = '/login';
//         return Promise.reject(err);
//       } finally {
//         isRefreshing = false;
//       }
//     }
//     return Promise.reject(error);
//   }
// );

// export default client;