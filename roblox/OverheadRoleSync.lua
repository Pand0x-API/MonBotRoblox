local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local API_URL = "https://TON-API-RENDER.onrender.com/api/player/"

local function updateRole(player)
    local character = player.Character or player.CharacterAdded:Wait()
    local head = character:WaitForChild("Head")
    local gui = head:WaitForChild("OverheadGui")

    local nameLabel = gui:WaitForChild("NameLabel")
    local roleLabel = gui:WaitForChild("RoleLabel")

    nameLabel.Text = player.Name

    local success, result = pcall(function()
        return HttpService:GetAsync(API_URL .. player.UserId)
    end)

    if not success then
        roleLabel.Visible = false
        return
    end

    local data = HttpService:JSONDecode(result)

    if data.role and data.role ~= "" then
        roleLabel.Visible = true
        roleLabel.Text = data.role

        if data.color then
            roleLabel.TextColor3 = Color3.fromRGB(
                data.color.r,
                data.color.g,
                data.color.b
            )
        end
    else
        roleLabel.Visible = false
    end
end

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(function()
        updateRole(player)
    end)
end)
