from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Team, Part, Aircraft, Production, AircraftPart, TEAM_TYPES, AIRCRAFT_TYPES, REQUIRED_PARTS
from django.utils import timezone
import json

class ModelTests(TestCase):
    def setUp(self):
        """Test için gerekli verileri oluşturur."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.team = Team.objects.create(name='Test Team', team_type='AVIONICS')
        self.team.members.add(self.user)
        self.part = Part.objects.create(
            name='Test Part',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=10,
            minimum_stock=5
        )
        self.aircraft = Aircraft.objects.create(
            aircraft_type='TB2',
            assembly_team=None
        )

    def test_team_can_produce_part(self):
        """Test that teams can only produce parts of their type"""
        self.assertTrue(self.team.can_produce_part(self.part))
        
        wrong_part = Part.objects.create(
            name='Wrong Part',
            team_type='BODY',
            aircraft_type='TB2',
            stock=10
        )
        self.assertFalse(self.team.can_produce_part(wrong_part))
        
        # Test that assembly team cannot produce any part
        assembly_team = Team.objects.create(name='Assembly Team', team_type='ASSEMBLY')
        self.assertFalse(assembly_team.can_produce_part(self.part))
        self.assertFalse(assembly_team.can_produce_part(wrong_part))

    def test_part_low_stock(self):
        """Test low stock detection"""
        self.assertFalse(self.part.is_low_stock)
        self.part.stock = 3
        self.part.save()
        self.assertTrue(self.part.is_low_stock)
        
        # Test zero stock
        self.part.stock = 0
        self.part.save()
        self.assertTrue(self.part.is_low_stock)
        
        # Test equal to minimum stock
        self.part.stock = 5
        self.part.save()
        self.assertFalse(self.part.is_low_stock)

    def test_aircraft_completion(self):
        """Test aircraft completion logic"""
        self.assertFalse(self.aircraft.is_complete)
        
        # Add required parts
        required = REQUIRED_PARTS['TB2']
        for team_type, count in required.items():
            part = Part.objects.create(
                name=f'Test {team_type}',
                team_type=team_type,
                aircraft_type='TB2',
                stock=count
            )
            for _ in range(count):
                self.aircraft.parts.add(part)
        
        self.assertTrue(self.aircraft.is_complete)
        
    def test_part_stock_management(self):
        """Test part stock increase and decrease methods"""
        initial_stock = self.part.stock
        
        # Test increase_stock
        self.part.increase_stock(5)
        self.assertEqual(self.part.stock, initial_stock + 5)
        
        # Test decrease_stock
        self.part.decrease_stock(3)
        self.assertEqual(self.part.stock, initial_stock + 5 - 3)
        
        # Test decrease_stock with insufficient stock
        with self.assertRaises(Exception):
            self.part.decrease_stock(100)
            
    def test_aircraft_add_part(self):
        """Test adding parts to aircraft"""
        assembly_team = Team.objects.create(name='Assembly Team', team_type='ASSEMBLY')
        self.aircraft.assembly_team = assembly_team
        self.aircraft.save()
        
        # Test adding a valid part
        initial_stock = self.part.stock
        aircraft_part = self.aircraft.add_part(self.part, self.user)
        
        # Check that part was added to aircraft
        self.assertIn(self.part, self.aircraft.parts.all())
        
        # Check that stock was decreased
        self.part.refresh_from_db()
        self.assertEqual(self.part.stock, initial_stock - 1)
        
        # Check that AircraftPart record was created correctly
        self.assertEqual(aircraft_part.aircraft, self.aircraft)
        self.assertEqual(aircraft_part.part, self.part)
        self.assertEqual(aircraft_part.added_by, self.user)
        
        # Test adding incompatible part
        wrong_part = Part.objects.create(
            name='Wrong Part',
            team_type='AVIONICS',
            aircraft_type='TB3',  # Different aircraft type
            stock=10
        )
        
        with self.assertRaises(Exception):
            self.aircraft.add_part(wrong_part, self.user)
            
        # Test adding part with insufficient stock
        zero_stock_part = Part.objects.create(
            name='Zero Stock Part',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=0
        )
        
        with self.assertRaises(Exception):
            self.aircraft.add_part(zero_stock_part, self.user)

class ViewTests(TestCase):
    def setUp(self):
        """Test için gerekli verileri oluşturur."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.team = Team.objects.create(name='Test Team', team_type='AVIONICS')
        self.team.members.add(self.user)
        
        # Create some parts
        self.part = Part.objects.create(
            name='Test Part',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=10,
            minimum_stock=5
        )
        
        # Create an aircraft
        self.aircraft = Aircraft.objects.create(
            aircraft_type='TB2',
            assembly_team=self.team
        )

    def test_login_required(self):
        """Test that views require login"""
        response = self.client.get(reverse('production:home'))
        self.assertEqual(response.status_code, 302)
        
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('production:home'))
        self.assertEqual(response.status_code, 200)

    def test_team_list_view(self):
        """Test team list view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('production:teams_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Team')
        
    def test_parts_list_view(self):
        """Test parts list view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('production:parts_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Part')
        
    def test_aircraft_list_view(self):
        """Test aircraft list view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('production:aircraft_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TB2')
        
    def test_profile_view(self):
        """Test profile view"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('production:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Team')

class APITests(APITestCase):
    def setUp(self):
        """Test için gerekli verileri oluşturur."""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        
        # Create teams
        self.avionics_team = Team.objects.create(name='Avionics Team', team_type='AVIONICS')
        self.avionics_team.members.add(self.user)
        
        self.assembly_team = Team.objects.create(name='Assembly Team', team_type='ASSEMBLY')
        
        # Create parts
        self.part = Part.objects.create(
            name='Test Part',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=10,
            minimum_stock=5
        )
        
        # Create aircraft
        self.aircraft = Aircraft.objects.create(
            aircraft_type='TB2',
            assembly_team=self.assembly_team
        )

    def test_parts_api(self):
        """Test parts API endpoints"""
        # Create part
        data = {
            'name': 'New Test Part',
            'team_type': 'AVIONICS',
            'aircraft_type': 'TB2',
            'stock': 10,
            'minimum_stock': 5
        }
        response = self.client.post(reverse('api:part-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get parts list
        response = self.client.get(reverse('api:part-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 parts now
        
        # Get part detail
        part_id = response.data['results'][0]['id']
        response = self.client.get(reverse('api:part-detail', args=[part_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Part')
        
        # Update part
        data = {
            'stock': 20,
            'minimum_stock': 10
        }
        response = self.client.patch(reverse('api:part-detail', args=[part_id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stock'], 20)
        
        # Test low stock endpoint
        self.part.stock = 3
        self.part.save()
        response = self.client.get(reverse('api:part-low-stock'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test part usage endpoint
        aircraft_part = AircraftPart.objects.create(
            aircraft=self.aircraft,
            part=self.part,
            added_by=self.user
        )
        response = self.client.get(reverse('api:part-usage', args=[self.part.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['usage_count'], 1)

    def test_team_production(self):
        """Test team production API endpoint"""
        part = Part.objects.create(
            name='Test Part',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=10
        )
        
        data = {
            'part': part.id,
            'quantity': 5
        }
        response = self.client.post(
            reverse('api:team-produce-part', args=[self.avionics_team.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        part.refresh_from_db()
        self.assertEqual(part.stock, 15)
        
        # Test production history
        response = self.client.get(reverse('api:team-production-history', args=[self.avionics_team.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test team members endpoint
        response = self.client.get(reverse('api:team-members', args=[self.avionics_team.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')
        
        # Test add member endpoint
        new_user = User.objects.create_user(username='newuser', password='newpass')
        data = {
            'user': new_user.id
        }
        response = self.client.post(reverse('api:team-add-member', args=[self.avionics_team.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.avionics_team.refresh_from_db()
        self.assertEqual(self.avionics_team.members.count(), 2)
        
        # Test remove member endpoint
        data = {
            'user': new_user.id
        }
        response = self.client.post(reverse('api:team-remove-member', args=[self.avionics_team.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.avionics_team.refresh_from_db()
        self.assertEqual(self.avionics_team.members.count(), 1)
        
    def test_aircraft_api(self):
        """Test aircraft API endpoints"""
        # Add user to assembly team
        self.assembly_team.members.add(self.user)
        
        # Create aircraft
        data = {
            'aircraft_type': 'TB2'
        }
        response = self.client.post(reverse('api:aircraft-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Get aircraft list
        response = self.client.get(reverse('api:aircraft-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # 2 aircraft now
        
        # Get aircraft detail
        aircraft_id = response.data['results'][0]['id']
        response = self.client.get(reverse('api:aircraft-detail', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['aircraft_type'], 'TB2')
        
        # Test add part endpoint
        part = Part.objects.create(
            name='Test Part for Aircraft',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=10
        )
        data = {
            'part': part.id
        }
        response = self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test parts summary endpoint
        response = self.client.get(reverse('api:aircraft-parts-summary', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('required_parts', response.data)
        self.assertIn('current_parts', response.data)
        
        # Test production history endpoint
        response = self.client.get(reverse('api:aircraft-production-history', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('history', response.data)
        
        # Test available parts endpoint
        response = self.client.get(reverse('api:aircraft-available-parts', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('parts', response.data)
        
        # Test complete production endpoint (should fail because not all parts are added)
        response = self.client.post(reverse('api:aircraft-complete-production', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Add all required parts
        required = REQUIRED_PARTS['TB2']
        for team_type, count in required.items():
            if team_type != 'AVIONICS':  # Already added one AVIONICS part
                part = Part.objects.create(
                    name=f'Test {team_type}',
                    team_type=team_type,
                    aircraft_type='TB2',
                    stock=count
                )
                for _ in range(count):
                    data = {
                        'part': part.id
                    }
                    self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
            else:
                # Add remaining AVIONICS parts
                for _ in range(required[team_type] - 1):  # -1 because we already added one
                    data = {
                        'part': part.id
                    }
                    self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
        
        # Now complete production should succeed
        response = self.client.post(reverse('api:aircraft-complete-production', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that aircraft is marked as completed
        response = self.client.get(reverse('api:aircraft-detail', args=[aircraft_id]))
        self.assertIsNotNone(response.data['completed_at'])

class IntegrationTests(APITestCase):
    """End-to-end integration tests for the production workflow."""
    
    def setUp(self):
        """Set up test data for the production workflow."""
        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='admin', is_staff=True)
        self.avionics_user = User.objects.create_user(username='avionics', password='avionics')
        self.body_user = User.objects.create_user(username='body', password='body')
        self.wing_user = User.objects.create_user(username='wing', password='wing')
        self.tail_user = User.objects.create_user(username='tail', password='tail')
        self.assembly_user = User.objects.create_user(username='assembly', password='assembly')
        
        # Create teams
        self.avionics_team = Team.objects.create(name='Avionics Team', team_type='AVIONICS')
        self.avionics_team.members.add(self.avionics_user)
        
        self.body_team = Team.objects.create(name='Body Team', team_type='BODY')
        self.body_team.members.add(self.body_user)
        
        self.wing_team = Team.objects.create(name='Wing Team', team_type='WING')
        self.wing_team.members.add(self.wing_user)
        
        self.tail_team = Team.objects.create(name='Tail Team', team_type='TAIL')
        self.tail_team.members.add(self.tail_user)
        
        self.assembly_team = Team.objects.create(name='Assembly Team', team_type='ASSEMBLY')
        self.assembly_team.members.add(self.assembly_user)
        
        # Create parts
        self.avionics_part = Part.objects.create(
            name='TB2 Avionics',
            team_type='AVIONICS',
            aircraft_type='TB2',
            stock=0,
            minimum_stock=5
        )
        
        self.body_part = Part.objects.create(
            name='TB2 Body',
            team_type='BODY',
            aircraft_type='TB2',
            stock=0,
            minimum_stock=5
        )
        
        self.wing_part = Part.objects.create(
            name='TB2 Wing',
            team_type='WING',
            aircraft_type='TB2',
            stock=0,
            minimum_stock=5
        )
        
        self.tail_part = Part.objects.create(
            name='TB2 Tail',
            team_type='TAIL',
            aircraft_type='TB2',
            stock=0,
            minimum_stock=5
        )
        
        # Create API client
        self.client = APIClient()
    
    def test_full_production_workflow(self):
        """Test the full production workflow from part production to aircraft completion."""
        # 1. Avionics team produces parts
        self.client.force_authenticate(user=self.avionics_user)
        data = {
            'part': self.avionics_part.id,
            'quantity': 10
        }
        response = self.client.post(
            reverse('api:team-produce-part', args=[self.avionics_team.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.avionics_part.refresh_from_db()
        self.assertEqual(self.avionics_part.stock, 10)
        
        # 2. Body team produces parts
        self.client.force_authenticate(user=self.body_user)
        data = {
            'part': self.body_part.id,
            'quantity': 15
        }
        response = self.client.post(
            reverse('api:team-produce-part', args=[self.body_team.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.body_part.refresh_from_db()
        self.assertEqual(self.body_part.stock, 15)
        
        # 3. Wing team produces parts
        self.client.force_authenticate(user=self.wing_user)
        data = {
            'part': self.wing_part.id,
            'quantity': 8
        }
        response = self.client.post(
            reverse('api:team-produce-part', args=[self.wing_team.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wing_part.refresh_from_db()
        self.assertEqual(self.wing_part.stock, 8)
        
        # 4. Tail team produces parts
        self.client.force_authenticate(user=self.tail_user)
        data = {
            'part': self.tail_part.id,
            'quantity': 5
        }
        response = self.client.post(
            reverse('api:team-produce-part', args=[self.tail_team.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tail_part.refresh_from_db()
        self.assertEqual(self.tail_part.stock, 5)
        
        # 5. Assembly team creates an aircraft
        self.client.force_authenticate(user=self.assembly_user)
        data = {
            'aircraft_type': 'TB2'
        }
        response = self.client.post(reverse('api:aircraft-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        aircraft_id = response.data['id']
        
        # 6. Assembly team adds parts to the aircraft
        # Add avionics parts
        for _ in range(REQUIRED_PARTS['TB2']['AVIONICS']):
            data = {
                'part': self.avionics_part.id
            }
            response = self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Add body parts
        for _ in range(REQUIRED_PARTS['TB2']['BODY']):
            data = {
                'part': self.body_part.id
            }
            response = self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Add wing parts
        for _ in range(REQUIRED_PARTS['TB2']['WING']):
            data = {
                'part': self.wing_part.id
            }
            response = self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Add tail parts
        for _ in range(REQUIRED_PARTS['TB2']['TAIL']):
            data = {
                'part': self.tail_part.id
            }
            response = self.client.post(reverse('api:aircraft-add-part', args=[aircraft_id]), data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 7. Check parts summary
        response = self.client.get(reverse('api:aircraft-parts-summary', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_complete'])
        
        # 8. Complete aircraft production
        response = self.client.post(reverse('api:aircraft-complete-production', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 9. Verify aircraft is completed
        response = self.client.get(reverse('api:aircraft-detail', args=[aircraft_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['completed_at'])
        
        # 10. Verify stock levels have decreased
        self.avionics_part.refresh_from_db()
        self.body_part.refresh_from_db()
        self.wing_part.refresh_from_db()
        self.tail_part.refresh_from_db()
        
        self.assertEqual(self.avionics_part.stock, 10 - REQUIRED_PARTS['TB2']['AVIONICS'])
        self.assertEqual(self.body_part.stock, 15 - REQUIRED_PARTS['TB2']['BODY'])
        self.assertEqual(self.wing_part.stock, 8 - REQUIRED_PARTS['TB2']['WING'])
        self.assertEqual(self.tail_part.stock, 5 - REQUIRED_PARTS['TB2']['TAIL']) 