import React, { useEffect, useRef } from 'react';
import './Home.css';
import VideoCard from './components/VideoCard';
import BottomNavbar from './components/BottomNavbar';
import TopNavbar from './components/TopNavbar';
import SwipeableProductCard from './components/SwipeableProductCard';
import { items } from './data';

const Product = () => {
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

export default Product;
