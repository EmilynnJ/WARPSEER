import { writable, derived } from 'svelte/store';
import { PUBLIC_BACKEND_URL } from '$env/static/public';

interface Notification {
  id: number;
  title: string;
  message: string;
  kind: string;
  is_read: boolean;
  created_at: string;
  action_url?: string;
}

interface NotificationStore {
  notifications: Notification[];
  unreadCount: number;
  permission: NotificationPermission | 'default';
  loading: boolean;
}

const createNotificationStore = () => {
  const { subscribe, set, update } = writable<NotificationStore>({
    notifications: [],
    unreadCount: 0,
    permission: 'default',
    loading: false
  });

  return {
    subscribe,
    
    async requestPermission() {
      if (!('Notification' in window)) {
        console.log('This browser does not support notifications');
        return false;
      }

      if (Notification.permission === 'granted') {
        await this.subscribeToPush();
        return true;
      }

      if (Notification.permission !== 'denied') {
        const permission = await Notification.requestPermission();
        update(state => ({ ...state, permission }));
        
        if (permission === 'granted') {
          await this.subscribeToPush();
          return true;
        }
      }
      
      return false;
    },

    async subscribeToPush() {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        return;
      }

      try {
        const registration = await navigator.serviceWorker.ready;
        
        // Check if already subscribed
        let subscription = await registration.pushManager.getSubscription();
        
        if (!subscription) {
          // Subscribe to push notifications
          subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(
              'YOUR_VAPID_PUBLIC_KEY' // Replace with actual VAPID key
            )
          });
        }

        // Send subscription to backend
        const token = localStorage.getItem('auth_token');
        await fetch(`${PUBLIC_BACKEND_URL}/api/notifications/subscribe`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            endpoint: subscription.endpoint,
            keys: {
              p256dh: arrayBufferToBase64(subscription.getKey('p256dh')),
              auth: arrayBufferToBase64(subscription.getKey('auth'))
            }
          })
        });
      } catch (error) {
        console.error('Failed to subscribe to push notifications:', error);
      }
    },

    async loadNotifications() {
      update(state => ({ ...state, loading: true }));
      
      try {
        const token = localStorage.getItem('auth_token');
        const res = await fetch(`${PUBLIC_BACKEND_URL}/api/notifications`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!res.ok) throw new Error('Failed to load notifications');
        
        const data = await res.json();
        update(state => ({
          ...state,
          notifications: data.notifications,
          unreadCount: data.notifications.filter((n: Notification) => !n.is_read).length,
          loading: false
        }));
      } catch (error) {
        console.error('Failed to load notifications:', error);
        update(state => ({ ...state, loading: false }));
      }
    },

    async markAsRead(notificationId: number) {
      const token = localStorage.getItem('auth_token');
      
      try {
        await fetch(`${PUBLIC_BACKEND_URL}/api/notifications/${notificationId}/read`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        update(state => ({
          ...state,
          notifications: state.notifications.map(n =>
            n.id === notificationId ? { ...n, is_read: true } : n
          ),
          unreadCount: Math.max(0, state.unreadCount - 1)
        }));
      } catch (error) {
        console.error('Failed to mark notification as read:', error);
      }
    },

    async markAllAsRead() {
      const token = localStorage.getItem('auth_token');
      
      try {
        await fetch(`${PUBLIC_BACKEND_URL}/api/notifications/read-all`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        update(state => ({
          ...state,
          notifications: state.notifications.map(n => ({ ...n, is_read: true })),
          unreadCount: 0
        }));
      } catch (error) {
        console.error('Failed to mark all notifications as read:', error);
      }
    },

    showInApp(title: string, message: string, action_url?: string) {
      // Create and show in-app notification toast
      const toast = document.createElement('div');
      toast.className = 'fixed top-4 right-4 max-w-sm bg-black/90 border border-mystic-purple rounded-lg p-4 shadow-lg z-50 animate-slide-in';
      
      toast.innerHTML = `
        <div class="flex items-start gap-3">
          <div class="flex-shrink-0">
            <svg class="w-6 h-6 text-mystic-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
          <div class="flex-1">
            <h4 class="font-semibold text-white">${title}</h4>
            <p class="text-sm text-gray-300 mt-1">${message}</p>
            ${action_url ? `<a href="${action_url}" class="text-mystic-pink text-sm hover:underline mt-2 inline-block">View Details</a>` : ''}
          </div>
          <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-white">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      `;
      
      document.body.appendChild(toast);
      
      // Auto remove after 5 seconds
      setTimeout(() => {
        toast.classList.add('animate-slide-out');
        setTimeout(() => toast.remove(), 300);
      }, 5000);
      
      // Also add to notifications list
      this.loadNotifications();
    }
  };
};

// Helper functions
function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return new Uint8Array(rawData.length).map((_, i) => rawData.charCodeAt(i));
}

function arrayBufferToBase64(buffer: ArrayBuffer | null) {
  if (!buffer) return '';
  const bytes = new Uint8Array(buffer);
  return window.btoa(String.fromCharCode(...bytes));
}

export const notifications = createNotificationStore();