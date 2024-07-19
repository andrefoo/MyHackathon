import React, { useEffect, useRef } from 'react';
import './App.css';
import VideoCard from './components/VideoCard';
import BottomNavbar from './components/BottomNavbar';
import TopNavbar from './components/TopNavbar';
import SwipeableProductCard from './components/SwipeableProductCard';

import video1 from './videos/video1.mp4';
import video2 from './videos/video2.mp4';
import video3 from './videos/video3.mp4';
import video4 from './videos/video4.mp4';
import image1 from './images/image1.png';

const items = [
  {
    type: 'video',
    url: video1,
    profilePic: 'https://p16-sign-useast2a.tiktokcdn.com/tos-useast2a-avt-0068-giso/9d429ac49d6d18de6ebd2a3fb1f39269~c5_100x100.jpeg?x-expires=1688479200&x-signature=pjH5pwSS8Sg1dJqbB1GdCLXH6ew%3D',
    username: 'csjackie',
    description: 'Lol nvm #compsci #chatgpt #ai #openai #techtok',
    song: 'Original sound - Famed Flames',
    likes: 430,
    comments: 13,
    saves: 23,
    shares: 1,
  },
  {
    type: 'product',
    productId: '1',
    productName: 'Red Leather Handbag',
    productDescription: 'Crafted with genuine leather. Synthetic lining. Detachable and adjustable shoulder strap. Approx. 20cm*15cm*7cm.',
    productImage: image1,
    productPrice: '99.00',
  },
  {
    type: 'video',
    url: video2,
    profilePic: 'https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/eace3ee69abac57c39178451800db9d5~c5_100x100.jpeg?x-expires=1688479200&x-signature=wAkVmwL7lej15%2B16ypSWQOqTP8s%3D',
    username: 'dailydotdev',
    description: 'Every developer brain @francesco.ciulla #developerjokes #programming #programminghumor #programmingmemes',
    song: 'tarawarolin wants you to know this isnt my sound - Chaplain J Rob',
    likes: '13.4K',
    comments: 3121,
    saves: 254,
    shares: 420,
  },
  {
    type: 'product',
    productId: '1',
    productName: 'Red Leather Handbag',
    productDescription: 'Crafted with genuine leather. Synthetic lining. Detachable and adjustable shoulder strap. Approx. 20cm*15cm*7cm.',
    productImage: image1,
    productPrice: '99.00',
  },
  {
    type: 'video',
    url: video3,
    profilePic: 'https://p77-sign-va.tiktokcdn.com/tos-maliva-avt-0068/4e6698b235eadcd5d989a665704daf68~c5_100x100.jpeg?x-expires=1688479200&x-signature=wkwHDKfNuIDqIVHNm29%2FRf40R3w%3D',
    username: 'wojciechtrefon',
    description: '#programming #softwareengineer #vscode #programmerhumor #programmingmemes',
    song: 'help so many people are using my sound - Ezra',
    likes: 5438,
    comments: 238,
    saves: 12,
    shares: 117,
  },
  {
    type: 'video',
    url: video4,
    profilePic: 'https://p16-sign-va.tiktokcdn.com/tos-maliva-avt-0068/4bda52cf3ad31c728153859262c329db~c5_100x100.jpeg?x-expires=1688486400&x-signature=ssUbbCpZFJj6uj33D%2BgtcqxMvgQ%3D',
    username: 'faruktutkus',
    description: 'Wait for the end | Im RTX 4090 TI | #softwareengineer #softwareengineer #coding #codinglife #codingmemes ',
    song: 'orijinal ses - Computer Science',
    likes: 9689,
    comments: 230,
    saves: 1037,
    shares: 967,
  },
];

const App = () => {
  const videoRefs = useRef([]);

  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.8,
    };

    const handleIntersection = (entries) => {
      entries.forEach((entry) => {
        const videoElement = entry.target;
        if (entry.isIntersecting) {
          videoElement.play();
        } else {
          videoElement.pause();
        }
      });
    };

    const observer = new IntersectionObserver(handleIntersection, observerOptions);

    const handleUserInteraction = () => {
      videoRefs.current.forEach((videoRef) => {
        if (videoRef) {
          observer.observe(videoRef);
        }
      });
      window.removeEventListener('click', handleUserInteraction);
      window.removeEventListener('touchstart', handleUserInteraction);
    };

    window.addEventListener('click', handleUserInteraction);
    window.addEventListener('touchstart', handleUserInteraction);

    return () => {
      observer.disconnect();
      window.removeEventListener('click', handleUserInteraction);
      window.removeEventListener('touchstart', handleUserInteraction);
    };
  }, []);

  const handleVideoRef = (index) => (ref) => {
    videoRefs.current[index] = ref;
  };

  const handleSwipeLeft = (item) => {
    // Handle swipe left action
  };

  const handleSwipeRight = (item) => {
    // Handle swipe right action
  };

  return (
    <div className="app">
      <div className="container">
        <TopNavbar />
        {items.map((item, index) => {
          if (item.type === 'video') {
            return (
              <VideoCard
                key={index}
                username={item.username}
                description={item.description}
                song={item.song}
                likes={item.likes}
                saves={item.saves}
                comments={item.comments}
                shares={item.shares}
                url={item.url}
                profilePic={item.profilePic}
                setVideoRef={handleVideoRef(index)}
                autoplay={index === 0}
              />
            );
          } else if (item.type === 'product') {
            return (
              <SwipeableProductCard
                key={index}
                product={item}
                onSwipeLeft={() => handleSwipeLeft(item)}
                onSwipeRight={() => handleSwipeRight(item)}
              />
            );
          }
          return null;
        })}
        <BottomNavbar />
      </div>
    </div>
  );
};

export default App;
