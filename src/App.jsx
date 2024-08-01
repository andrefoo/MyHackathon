import React, { useState } from 'react';
import { useSwipeable } from 'react-swipeable';
import './App.css';
import Home from './home';
import Product from './product';

const App = () => {
  const [showHome, setShowHome] = useState(true);
  const [swipeClass, setSwipeClass] = useState('');

  const handlers = useSwipeable({
    onSwipedRight: () => {
      setSwipeClass('swipe-right');
      setTimeout(() => {
        setShowHome(false);
        setSwipeClass('');
      }, 300); // Duration of the swipe animation
    }
  });

  return (
    <div {...handlers} className={`swipe-container ${swipeClass}`}>
      {showHome ? <Home /> : <Product />}
    </div>
  );
};

export default App;
