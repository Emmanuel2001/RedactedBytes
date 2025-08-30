"use client"

import { Calendar, Home, Inbox, Search, Settings, ChevronUp, User2, Sun, MoonStar, Monitor, Video, Image } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/sidebar"

import {DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem} from "@/components/ui/dropdown-menu"
import { useTheme } from "./ThemeProvider"

// Menu items.
const items = [
  {
    title: "Image",
    url: "/",
    icon: Image,
  },
  {
    title: "Video",
    url:"/video",
    icon: Video
  }
]

export function AppSidebar() {
  const { theme, setTheme } = useTheme();
  
  return (
    <Sidebar className="h-screen flex flex-col">
      <SidebarContent className="flex-grow">
        <SidebarGroup>
          <SidebarGroupLabel>Application</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="border-t mt-auto">
        <SidebarMenu>
          {/* Custom Theme Selector */}
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  {theme === "light" && <Sun className="h-4 w-4 mr-2 text-yellow-400 fill-yellow-400" />}
                  {theme === "dark" && <MoonStar className="h-4 w-4 mr-2 text-blue-400" />}
                  {theme === "system" && <Monitor className="h-4 w-4 mr-2 text-gray-400" />}
                  <span>Appearance</span>
                  <ChevronUp className="h-4 w-4 ml-auto" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                side="top"
                className="w-[--radix-popper-anchor-width]"
              >
                <DropdownMenuItem onClick={() => setTheme("light")}>
                  <Sun className="h-4 w-4 mr-2 text-yellow-400 fill-yellow-400" />
                  <span>Light Mode</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme("dark")}>
                  <MoonStar className="h-4 w-4 mr-2 text-blue-400" />
                  <span>Dark Mode</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setTheme("system")}>
                  <Monitor className="h-4 w-4 mr-2 text-gray-400" />
                  <span>System Default</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
          
          {/* User Account Menu */}
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton>
                  <User2 className="h-4 w-4 mr-2" /> 
                  <span>Username</span>
                  <ChevronUp className="h-4 w-4 ml-auto" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                side="top"
                className="w-[--radix-popper-anchor-width]"
              >
                <DropdownMenuItem>
                  <span>Account</span>
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <span>Sign out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}