import { AppProps } from 'next/app';
import Head from 'next/head';
import '../styles/globals.css';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import useStore from '../store/useStore';
import Auth from '../components/Auth';
import useNotificationSimulator from '../hooks/useNotificationSimulator';

function MyApp({ Component, pageProps }: AppProps) {
  const { isAuthenticated } = useStore();
  useNotificationSimulator();

  return (
    <>
      <Head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700&display=swap" rel="stylesheet" />
      </Head>
      {isAuthenticated ? <Component {...pageProps} /> : <Auth />}
    </>
  );
}

export default MyApp;
