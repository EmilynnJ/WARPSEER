<script lang="ts">
  import { onMount } from 'svelte';
  import { notifications } from '$lib/stores/notifications';
  
  let notificationStore: any;
  let enableNotifications = false;
  let notificationTypes = {
    session_request: true,
    appointment_reminder: true,
    payment_received: true,
    new_message: true,
    stream_started: true
  };
  
  notifications.subscribe(value => {
    notificationStore = value;
  });
  
  onMount(async () => {
    // Check current permission status
    if ('Notification' in window) {
      enableNotifications = Notification.permission === 'granted';
    }
    
    // Load user notification preferences from backend
    loadPreferences();
  });
  
  async function toggleNotifications() {
    if (enableNotifications) {
      // Request permission
      const granted = await notifications.requestPermission();
      if (!granted) {
        enableNotifications = false;
        alert('Please enable notifications in your browser settings');
      }
    } else {
      // Disable notifications (unsubscribe)
      // This would typically call a backend endpoint to remove the subscription
      alert('Notifications disabled');
    }
  }
  
  async function loadPreferences() {
    // Load user's notification preferences from backend
    // This is a placeholder - implement actual API call
  }
  
  async function savePreferences() {
    // Save notification preferences to backend
    // This is a placeholder - implement actual API call
    alert('Notification preferences saved');
  }
  
  function testNotification() {
    notifications.showInApp(
      'Test Notification',
      'This is a test notification to verify everything is working correctly.',
      '/settings/notifications'
    );
  }
</script>

<svelte:head>
  <title>Notification Settings - SoulSeer</title>
</svelte:head>

<div class="min-h-screen bg-mystic-dark text-white p-4">
  <div class="max-w-2xl mx-auto">
    <h1 class="text-4xl font-script text-mystic-pink mb-8">Notification Settings</h1>
    
    <!-- Enable/Disable Toggle -->
    <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple mb-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-xl font-semibold mb-2">Push Notifications</h2>
          <p class="text-gray-400 text-sm">
            Receive real-time notifications for important events
          </p>
        </div>
        <label class="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            bind:checked={enableNotifications}
            on:change={toggleNotifications}
            class="sr-only peer"
          />
          <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-mystic-pink"></div>
        </label>
      </div>
      
      {#if enableNotifications}
        <button
          on:click={testNotification}
          class="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition text-sm"
        >
          Send Test Notification
        </button>
      {/if}
    </div>
    
    <!-- Notification Types -->
    {#if enableNotifications}
      <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple mb-6">
        <h2 class="text-xl font-semibold mb-4">Notification Types</h2>
        <div class="space-y-4">
          <label class="flex items-center justify-between">
            <div>
              <div class="font-medium">Session Requests</div>
              <div class="text-sm text-gray-400">When a client requests a reading session</div>
            </div>
            <input
              type="checkbox"
              bind:checked={notificationTypes.session_request}
              class="w-4 h-4 text-mystic-pink bg-gray-700 border-gray-600 rounded focus:ring-mystic-pink"
            />
          </label>
          
          <label class="flex items-center justify-between">
            <div>
              <div class="font-medium">Appointment Reminders</div>
              <div class="text-sm text-gray-400">Reminders before scheduled appointments</div>
            </div>
            <input
              type="checkbox"
              bind:checked={notificationTypes.appointment_reminder}
              class="w-4 h-4 text-mystic-pink bg-gray-700 border-gray-600 rounded focus:ring-mystic-pink"
            />
          </label>
          
          <label class="flex items-center justify-between">
            <div>
              <div class="font-medium">Payment Received</div>
              <div class="text-sm text-gray-400">When you receive payments or tips</div>
            </div>
            <input
              type="checkbox"
              bind:checked={notificationTypes.payment_received}
              class="w-4 h-4 text-mystic-pink bg-gray-700 border-gray-600 rounded focus:ring-mystic-pink"
            />
          </label>
          
          <label class="flex items-center justify-between">
            <div>
              <div class="font-medium">New Messages</div>
              <div class="text-sm text-gray-400">Direct messages from clients or readers</div>
            </div>
            <input
              type="checkbox"
              bind:checked={notificationTypes.new_message}
              class="w-4 h-4 text-mystic-pink bg-gray-700 border-gray-600 rounded focus:ring-mystic-pink"
            />
          </label>
          
          <label class="flex items-center justify-between">
            <div>
              <div class="font-medium">Stream Started</div>
              <div class="text-sm text-gray-400">When your favorite readers start streaming</div>
            </div>
            <input
              type="checkbox"
              bind:checked={notificationTypes.stream_started}
              class="w-4 h-4 text-mystic-pink bg-gray-700 border-gray-600 rounded focus:ring-mystic-pink"
            />
          </label>
        </div>
        
        <button
          on:click={savePreferences}
          class="mt-6 bg-gradient-to-r from-mystic-pink to-mystic-purple px-6 py-2 rounded-lg hover:opacity-90 transition"
        >
          Save Preferences
        </button>
      </div>
    {/if}
    
    <!-- Recent Notifications -->
    <div class="bg-black/50 rounded-lg p-6 border border-mystic-purple">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Recent Notifications</h2>
        {#if notificationStore?.unreadCount > 0}
          <button
            on:click={() => notifications.markAllAsRead()}
            class="text-sm text-mystic-pink hover:underline"
          >
            Mark all as read
          </button>
        {/if}
      </div>
      
      {#if notificationStore?.loading}
        <div class="flex justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-mystic-pink"></div>
        </div>
      {:else if notificationStore?.notifications.length === 0}
        <p class="text-gray-400 text-center py-8">No notifications yet</p>
      {:else}
        <div class="space-y-3">
          {#each notificationStore.notifications.slice(0, 10) as notification}
            <div
              class="p-3 rounded-lg border {notification.is_read ? 'bg-black/30 border-gray-700' : 'bg-mystic-purple/10 border-mystic-purple'}"
              on:click={() => !notification.is_read && notifications.markAsRead(notification.id)}
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <h4 class="font-medium {!notification.is_read && 'text-mystic-pink'}">
                    {notification.title}
                  </h4>
                  <p class="text-sm text-gray-400 mt-1">{notification.message}</p>
                </div>
                <span class="text-xs text-gray-500">
                  {new Date(notification.created_at).toLocaleDateString()}
                </span>
              </div>
              {#if notification.action_url}
                <a
                  href={notification.action_url}
                  class="text-sm text-mystic-pink hover:underline mt-2 inline-block"
                >
                  View Details →
                </a>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Custom checkbox styles */
  input[type="checkbox"]:checked {
    background-color: #ff69b4;
    border-color: #ff69b4;
  }
</style>