import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faHouse,
  faUserFriends,
  faPlus,
  faInbox,
  fa7,
  faUser,
} from '@fortawesome/free-solid-svg-icons';

const navItems = [
  { icon: faHouse, label: 'Home', isActive: true },
  { icon: faUserFriends, label: 'Friends', isActive: false },
  { icon: faPlus, label: 'Create', isActive: false, isPlus: true },
  { icon: faInbox, label: 'Inbox', isActive: false, hasNotification: true },
  { icon: faUser, label: 'Profile', isActive: false },
];

const BottomNavbar = () => {
  return (
    <div className="bottom-navbar">
      {navItems.map(({ icon, label, isActive, isPlus, hasNotification }, index) => (
        <div key={index} className={`nav-item ${isActive ? 'active' : ''}`}>
          {hasNotification && <FontAwesomeIcon icon={fa7} className="notification" />}
          <FontAwesomeIcon icon={icon} className={`icon ${isPlus ? 'plus' : ''}`} />
          <span className={`item-name ${isActive ? 'active' : ''}`}>{label}</span>
        </div>
      ))}
    </div>
  );
};

export default BottomNavbar;
