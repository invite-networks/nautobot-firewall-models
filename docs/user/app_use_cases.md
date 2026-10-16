# Using the App

This document describes common use-cases and scenarios for this App.

## General Usage

A detailed walkthrough is provided in the [Introducing Nautobot Firewall Models](https://blog.networktocode.com/post/nautobot-firewall-models/) blog post.

### Assigning Policies

Policies (`Policy` or `NATPolicy` objects) are assigned to firewalls, under Security > Appliances:

- Create a `Firewall` for each PAN-OS firewall, bound to its Device or Virtual Machine.
- Pair two Firewalls in an `HAGroup`, with the management address they share.
- Collect Firewalls and HA Groups in a `FirewallGroup` to assign a policy to all of them at once.
- Assign each policy to Firewalls, HA Groups or Firewall Groups in its Assigned To field. A Firewall in an HA Group is assigned through its HA Group.

Although policies can be created without any rules it is recommended to create the required underlying objects first before moving to the policy definitions. [Creation Order](../dev/models.md#creation-order) provides an ordered list of steps for creating and assigning, objects, needed for policy creation.

## Use-cases and common workflows

For examples of REST and GraphQL API usage see the [External Interactions](external_interactions.md) page.

## Screenshots

![Navigation Menu](../images/navmenu.png#only-light "Navigation Menu"){ .on-glb }
![Navigation Menu](../images/navmenu.png#only-dark "Navigation Menu"){ .on-glb }

![Policy View](../images/policy-light.png#only-light "Policy View"){ .on-glb }
![Policy View](../images/policy-dark.png#only-dark "Policy View"){ .on-glb }
[//]: # "`https://next.demo.nautobot.com/plugins/firewall/policy/423c6387-59e2-4573-a5c5-dc646b024dd3/?tab=policy-rules`"
