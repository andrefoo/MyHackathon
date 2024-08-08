import React from 'react';
import PropTypes from 'prop-types';
import { useSwipeable } from 'react-swipeable';
import './SwipeableProductCard.css';
import iconsOng from './icons.ong.png'; // Adjust the path as needed
import refreshIcon from '../images/refresh.png';
import crossIcon from '../images/cross.png';
import cartIcon from '../images/cart.png';
import likeIcon from '../images/like.png';
import saveIcon from '../images/save.png';

const SwipeableProductCard = ({ product, onSwipeLeft, onSwipeRight }) => {
  const handlers = useSwipeable({
    onSwipedLeft: () => onSwipeLeft(product),
    onSwipedRight: () => onSwipeRight(product),
    preventDefaultTouchmoveEvent: true, // Ensure default touchmove is prevented
    trackMouse: true,
  });

  return (
    <div {...handlers} className="product-card">
      <div className="product-image-container">
        <img
          className="product-image"
          src={product.productImage}
          alt={product.productName}
        />
      </div>
      <div className="product-info">
        <h2>
          {product.productName} <span className="product-rating">4.3⭐️</span>
        </h2>
        <p>{product.productDescription}</p>
        <p className="product-price">${product.productPrice}</p>
      </div>
      <div className="product-actions">
        <button className="action-btn" onClick={() => console.log('Refresh')}>
          <img src={refreshIcon} alt="Refresh" />
        </button>
        <button className="action-btn" onClick={() => onSwipeLeft(product)}>
          <img src={crossIcon} alt="Cross" />
        </button>
        <button className="action-btn" onClick={() => console.log('Add to Cart')}>
          <img src={cartIcon} alt="Cart" />
        </button>
        <button className="action-btn" onClick={() => onSwipeRight(product)}>
          <img src={likeIcon} alt="Like" />
        </button>
        <button className="action-btn" onClick={() => console.log('Save')}>
          <img src={saveIcon} alt="Save" />
        </button>
      </div>
    </div>
  );
};

SwipeableProductCard.propTypes = {
  product: PropTypes.shape({
    productName: PropTypes.string.isRequired,
    productDescription: PropTypes.string.isRequired,
    productPrice: PropTypes.number.isRequired,
    productImage: PropTypes.string.isRequired,
  }).isRequired,
  onSwipeLeft: PropTypes.func.isRequired,
  onSwipeRight: PropTypes.func.isRequired,
};

export default SwipeableProductCard;
