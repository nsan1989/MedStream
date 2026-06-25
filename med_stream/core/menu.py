from facilities.models import Facility

MENU_ITEMS = {
    "SUPER_ADMIN": [
        {
            "icon": "house",
            "menu_name": "Dashboard",
            "menu_link": "/accounts/super_admin_dashboard/",
        },
        {
            "icon": "building",
            "menu_name": "Organizations",
            "menu_link": "/organizations/all_org/",
        },
        {
            "icon": "box",
            "menu_name": "Audit",
            "menu_link": "/audits/audit_logs/",
        },
        {"icon": "wallet", "menu_name": "Revenue", "menu_link": "/revenue/"},
        {
            "icon": "person",
            "menu_name": "Profile",
            "menu_link": "/accounts/profile/",
        },
        {
            "icon": "gear",
            "menu_name": "Settings",
            "menu_link": "/settings/",
        },
    ],
    "ADMIN": [
        {
            "icon": "house",
            "menu_name": "Dashboard",
            "menu_link": "/accounts/admin_dashboard/",
        },
        {
            "icon": "hospital",
            "menu_name": "Facilities",
            "menu_link": "/facility/facilities/",
        },
        {
            "icon": "display",
            "menu_name": "Devices",
            "menu_link": "/device/all_devices/",
        },
        {
            "icon": "people",
            "menu_name": "Staff",
            "menu_link": "/organizations/org_staff/",
        },
        {
            "icon": "person",
            "menu_name": "Profile",
            "menu_link": "/accounts/profile/",
        },
        {
            "icon": "box",
            "menu_name": "Audit",
            "menu_link": "/audits/audit_logs/",
        },
        {
            "icon": "gear",
            "menu_name": "Settings",
            "sub_menu": [
                {
                    "icon": "plus",
                    "menu_name": "Add Staff",
                    "menu_link": "/facility/settings/add_staff/",
                },
                {
                    "icon": "plus",
                    "menu_name": "Add Facility",
                    "menu_link": "/facility/settings/add_facility/",
                },
            ],
        },
    ],
    "STAFF": [
        {
            "icon": "house",
            "menu_name": "Dashboard",
            "menu_link": "/accounts/staff_dashboard/",
        },
        {"icon": "buildings", "menu_name": "Block", "menu_link": "/facility/blocks/"},
        {"icon": "layers", "menu_name": "Floor", "menu_link": "/facility/floors/"},
        {
            "icon": "display",
            "menu_name": "Devices",
            "menu_link": "/device/all_devices/",
        },
        {
            "icon": "calendar3",
            "menu_name": "Schedules",
            "menu_link": "/schedule/all_schedules/",
        },
        {
            "icon": "collection-play",
            "menu_name": "Media",
            "menu_link": "/media/media_list/",
        },
        {
            "icon": "play",
            "menu_name": "Playlist",
            "menu_link": "/playlist/all_playlist/",
        },
        {
            "icon": "megaphone",
            "menu_name": "Broadcasting",
            "menu_link": "/broadcasting/",
        },
        {
            "icon": "exclamation-triangle",
            "menu_name": "Emergency",
            "menu_link": "/emergency/",
        },
        {
            "icon": "person",
            "menu_name": "Profile",
            "menu_link": "/accounts/profile/",
        },
        {
            "icon": "gear",
            "menu_name": "Settings",
            "sub_menu": [
                {
                    "icon": "plus",
                    "menu_name": "Add Department",
                    "menu_link": "/schedule/settings/add_department/",
                },
                {
                    "icon": "plus",
                    "menu_name": "Add Doctor",
                    "menu_link": "/schedule/settings/add_doctor/",
                },
                {
                    "icon": "plus",
                    "menu_name": "Add Block",
                    "menu_link": "/facility/settings/add_block/",
                },
                {
                    "icon": "plus",
                    "menu_name": "Add Floor",
                    "menu_link": "/facility/settings/add_floor/",
                },
                {
                    "icon": "plus",
                    "menu_name": "Add Device",
                    "menu_link": "/device/settings/add_device/",
                },
            ],
        },
    ],
}
