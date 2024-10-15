class StatusStore {
  constructor() {
    this.store = new Set();
  }

  add(value) {
    // Check if the value is already in the set
    if (!this.store.has(value)) {
      this.store.add(value);
      return true;
    }
    return false;
  }

  remove(value) {
    // Check if the value is in the set
    if (this.store.has(value)) {
      this.store.delete(value);
      return true;
    }
    return false;
  }

  getAll() {
    // Return an array of all values in the set
    return Array.from(this.store);
  }

  status(value) {
    // Check if the value exists in the set
    return this.store.has(value);
  }

  clear() {
    // Clear all statuses from the store
    this.store.clear();
  }
}

export default StatusStore;

//   // Example usage:
//   const myStore = new StatusStore();
//   console.log(myStore.add("online")); // true
//   console.log(myStore.add("offline")); // true
//   console.log(myStore.add("online")); // false (duplicate)
//   console.log(myStore.getAll()); // ["online", "offline"]
//   console.log(myStore.status("online")); // true
//   console.log(myStore.status("away")); // false
//   console.log(myStore.remove("online")); // true
//   console.log(myStore.getAll()); // ["offline"]
//   console.log(myStore.status("online")); // false (already removed)
//   myStore.clear();
//   console.log(myStore.getAll()); // []
