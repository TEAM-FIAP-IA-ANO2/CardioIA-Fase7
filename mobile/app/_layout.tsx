import {Stack} from 'expo-router';import {StatusBar} from 'expo-status-bar';
export default function Layout(){return <><StatusBar style="light"/><Stack screenOptions={{headerStyle:{backgroundColor:'#071a2a'},headerTintColor:'#fff',contentStyle:{backgroundColor:'#06131e'}}}><Stack.Screen name="index" options={{title:'CardioIA'}}/></Stack></>}
