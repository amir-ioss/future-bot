import React, { createContext, useContext, useReducer } from "react";
export const saveToStorage = (key = "@user", state) => {
    try {
        const serialisedState = JSON.stringify(state);
        localStorage.setItem(key, serialisedState);
        // console.log('SAVING LOCALSTORAGE', key, state)
    } catch (e) {
        console.warn(e);
    }
};

// Create a context for your store
const StoreContext = createContext();

// Create a custom hook to access the store
export const useStore = () => {
    const context = useContext(StoreContext);
    if (!context) {
        throw new Error("useStore must be used within a StoreProvider");
    }
    return context;
};

// Create a provider for your store
export const StoreProvider = ({ children }) => {
    const initialState = {
        events: ["this is test from abbasy"],
        activeCand: null,

    };

    // Define a reducer function to update the state
    const reducer = (state, action) => {
        switch (action.type) {
            case "set_event":
                return { ...state, events: [...state.events, action.payload] };
            case "set_event_clear":
                return { ...state, events: [] };
            case "set_active_cand":
                return { ...state, activeCand: action.payload };
            default:
                return state;
        }
    };

    const [state, dispatch] = useReducer(reducer, initialState);

    const setEvent = (e) => {
        dispatch({
            type: "set_event",
            payload: e,
        });
    };

    const setActiveCand = (e) => {
        dispatch({
            type: "set_active_cand",
            payload: e,
        });
    };

    const setEventClear = () => {
        dispatch({
            type: "set_event_clear",
        });
    }


    const value = {
        ...state,
        dispatch,
        setEvent,
        setActiveCand,
        setEventClear
    };

    return (
        <StoreContext.Provider value={value}>{children}</StoreContext.Provider>
    );
};
