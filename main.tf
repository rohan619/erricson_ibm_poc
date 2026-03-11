# write a terraform script to create a VM and vpc in google cloud

provider "google" {
  project = "your-project-id"
  region  = "us-central1"
}

resource "google_compute_network" "vpc_network" {
  name                    = "vpc-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnetwork" {
  name          = "subnetwork"
  ip_cidr_range = "10.0.0.0/24"
  region       = "us-central1"
  network      = google_compute_network.vpc_network.id
}

resource "google_compute_instance" "vm_instance" {
  name         = "vm-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.subnetwork.id

    access_config {
      // Ephemeral public IP
    }
  }
}