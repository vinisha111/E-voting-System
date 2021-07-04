from django.shortcuts import render, redirect
from django.contrib import messages
from pages.models import Voter, Admin, System, TallyingAuthority, Candidate
import http
from random import randint
import helper
import logging
import math
from decimal import Decimal

logger = logging.getLogger(__name__)
system = System.objects.all()[0]
candidates = Candidate.objects.all()
tallying_authorities = TallyingAuthority.objects.all()

###############################################
## VOTER
###############################################


def voter_registration(request):
    parent_path = "voter/"

    context = {
        "page_title": "Voter Registration",
        "parent_path": parent_path
    }

    if system.voter_registration_open is False:
        messages.error(request, f"Voter registration window is closed now.")
        return render(request, 'register.html', context)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        id_number = request.POST.get('id_number')

        try:

            voter = Voter.objects.get(email=email, identity_number=id_number)
            if voter.is_registered:
                messages.error(request, f"You are already registered in the system, please login using your email and password.")
                return render(request, 'register.html', context)

            voter.name = name
            voter.password = password
            voter.is_registered = True

            candidates = Candidate.objects.all()
            r = generate_voter_reference(candidates)
            A, B = encrypt_voter_reference(system, r)
            print("here1")
            voter.reference = r
            voter.a_reference = A
            voter.b_reference = B
            voter.save()

            return redirect("/" + parent_path + "login/")

        except Exception as e:
            # messages.error(request, f"User not found. Either the Email or ID Number is incorrect")
            messages.error(request, e)
            return render(request, 'register.html', context)

    return render(request, 'register.html', context)

def voter_login(request):
    parent_path = "voter/"
    context = {
        "page_title": "Voter Login",
        "parent_path": parent_path
    }

    try:
        if request.session['admin_email'] is not None :
            try:
                _ =  Voter.objects.get(email=request.session['admin_email'])
                return redirect("/" + parent_path + "home/")
            except Exception as _:
                pass
    except KeyError:
        pass

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            _ = Voter.objects.get(email=email)
        except Exception as _:
            messages.error(request, f"User not found.")
            return render(request, 'login.html', context)
            
        try:
            _ = Voter.objects.get(email=email, password=password)
            request.session['admin_email'] = email
            return redirect("/" + parent_path + "home/")
        except Exception as _:
            messages.error(request, f"Invalid credentials.")
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html', context)

def voter_dashboard(request):
    context = {}

    try:
        if request.session['admin_email'] is not None :
            try:
                voter = Voter.objects.get(email=request.session['admin_email'])
                parent_path = "voter/"
                candidates = Candidate.objects.all()

                if request.method == 'POST':
                    candidate_id = request.POST.get('candidate_id')
                    
                    vote = ""
                    vote_enc = ""
                    ref = voter.reference

                    for i in range(len(candidates)):
                        if int(candidate_id) == int(candidates[i].id) :
                            vote += "1"
                        else :
                            vote += "0"

                        if vote[i] == ref[i] :
                            vote_enc += "-1,"
                        else :
                            vote_enc += "1,"

                    print("\n\n" + voter.name + "'s vote: " + str(vote))
                    voter.vote = vote_enc
                    voter.has_voted = True
                    voter.save()

                context = {
                    "admin_name": voter.name.upper(),
                    "parent_path": parent_path,
                    "system": system,
                    "candidates": candidates,
                    "has_voted": voter.has_voted,
                    "reference": voter.reference.replace("0","-1")
                }

            except Exception as _:
                voter_logout(request)
    except KeyError:
        voter_logout(request)

    return render(request, 'index.html', context)


###############################################
## TALLYING AUTHORITY
###############################################


def tallying_authority_registration(request):
    context = {
        "page_title": "Tallying Authority Registration",
        "parent_path": "tallyingauthority/"
    }

    if system.tallying_authority_registration_open is False:
        messages.error(request, f"Registration window for Tallying Authority is closed now.")
        return render(request, 'tallying_authority_register.html', context)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        id_number = request.POST.get('id_number')
        
        try:
            tallying_authority = TallyingAuthority.objects.get(email=email, identity_number=id_number)
            if tallying_authority.is_registered:
                messages.error(request, f"You are already registered in the system, please login using your email and password.")
                return render(request, 'tallying_authority_register.html', context)

            tallying_authority.name = name
            tallying_authority.password = password
            tallying_authority.is_registered = True

            x = randint(1, int(system.q)-1)
            tallying_authority.private_key = x
            tallying_authority.public_key = pow(int(system.g), x)

            tallying_authority.save()

            logger.error("Tallying Authority Private Key: " + str(tallying_authority.private_key))
            logger.error("Tallying Authority Public Key: " + str(tallying_authority.public_key))

            # Redirect to tallying authority dashboard

        except Exception as _:
            messages.error(request, f"User not found. Either the Email or ID Number is incorrect")
            return render(request, 'tallying_authority_register.html', context)

    return render(request, 'tallying_authority_register.html', context)

def tallying_authority_login(request):
    parent_path = "tallyingauthority/"
    context = {
        "page_title": "Tallying Authority Login",
        "parent_path": parent_path
    }

    try:
        if request.session['admin_email'] is not None :
            try:
                _ =  TallyingAuthority.objects.get(email=request.session['admin_email'])
                return redirect("/" + parent_path + "home/")
            except Exception as _:
                pass
    except KeyError:
        pass

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            _ = TallyingAuthority.objects.get(email=email)
        except Exception as _:
            messages.error(request, f"User not found.")
            return render(request, 'tallying_authority_login.html', context)

        try:
            _ = TallyingAuthority.objects.get(email=email, password=password)
            request.session['admin_email'] = email
            return redirect("/" + parent_path + "home/")
        except Exception as _:
            messages.error(request, f"Invalid credentials.")
            return render(request, 'tallying_authority_login.html', context)
    else:
        return render(request, 'tallying_authority_login.html', context)

def tallying_authority_dashboard(request):
    parent_path = "tallyingauthority/"

    context = {
        "admin_name": "",
        "parent_path": parent_path
    }

    try:
        if request.session['admin_email'] is not None :  
            try:
                t_authority =  TallyingAuthority.objects.get(email=request.session['admin_email'])  
                candidates = Candidate.objects.all()

                if request.method == 'POST':
                    submit_result = request.POST.get('submit_result')
                    if submit_result == "true":
                        x_val = ""
                        for j in range(len(candidates)):
                            x = pow(Decimal(candidates[j].xnt), Decimal(t_authority.private_key))
                            x_val += str(x) + ","
                        
                        t_authority.x_value = x_val
                        t_authority.result_submitted = True

                        t_authority.save()

                        if len(TallyingAuthority.objects.filter(result_submitted=False)) == 0:
                            tallying_authorities = TallyingAuthority.objects.all()
                            print("\n\n\n\n\n\n\n\n")
                            for j in range(len(candidates)):
                                eq = 1
                                for t in range(len(tallying_authorities)):
                                    xij_str = tallying_authorities[t].x_value.split(",")
                                    eq *= pow(Decimal(xij_str[j]),-1)
                                eq *= Decimal(candidates[j].ynt)

                                zj = math.log(eq)/math.log(Decimal(system.g))
                                voters = Voter.objects.all()
                                yj = (zj + len(voters))/2
                                nj = len(voters) - yj

                                candidates[j].yes_count = str(yj)
                                candidates[j].no_count = str(nj)
                                candidates[j].save()

                                print("\n\n------------------------------------------------------------------------")
                                print(candidates[j].name + "'s YES count: " + str(yj))
                                print(candidates[j].name + "'s NO count: " + str(nj))
                                print("------------------------------------------------------------------------\n\n")

                context = {
                    "admin_name": t_authority.name.upper(),
                    "parent_path": parent_path,
                    "private_key": t_authority.private_key,
                    "voting_enabled": system.voting_enabled,
                    "result_submitted": t_authority.result_submitted,
                    "candidate_xnt": candidates[0].xnt,
                    "candidates": candidates
                }

            except Exception as e:
                print(e)
                tallying_authority_logout(request)
    except KeyError:
        tallying_authority_logout(request)
    
    return render(request, 'tallying_authority_dashboard.html', context)


###############################################
## ADMIN
###############################################

def admin_login(request):
    # clear_votes()
    parent_path = "administrator/"
    context = {
        "parent_path": parent_path
    }

    try: 
        if request.session['admin_email'] is not None :
            try:
                _ =  Admin.objects.get(email=request.session['admin_email'])
                return redirect("/" + parent_path + "home/")
            except Exception as _:
                pass
    except KeyError:
        pass

    admins = Admin.objects.all()
    if len(admins) == 0:
        a = Admin(name="Haider Mirza", email="haider.a.mirza94@gmail.com", password="haider")

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            _ = Admin.objects.get(email=email)
        except Exception as _:
            messages.error(request, f"User not found.")
            return render(request, 'admin_login.html', context)


        try:
            _ = Admin.objects.get(email=email, password=password)
            request.session['admin_email'] = email
            return redirect("/" + parent_path + "home/")
        except Exception as _:
            messages.error(request, f"Invalid credentials.")
            return render(request, 'admin_login.html', context)
    else:
        return render(request, 'admin_login.html', context)

def admin_dashboard(request):
    parent_path = "administrator/"
    context = {
        "parent_path": parent_path,
        "system": system
    }

    try: 
        if request.session['admin_email'] is not None :
            try:
                admin =  Admin.objects.get(email=request.session['admin_email'])
                context = {
                    "admin_name": admin.name.upper(),
                    "parent_path": parent_path,
                    "system": system
                }
            except Exception as _:
                admin_logout(request)
    except KeyError:
        admin_logout(request)
    
    if request.method == 'POST':
        logout = request.POST.get('logout')
        sender_type = request.POST.get('sender_type')
        if sender_type is not None:
            if sender_type == "voter_registration":
                if system.voter_registration_open is True:
                    system.voter_registration_open = False
                else:
                    system.voter_registration_open = True
            elif sender_type == "voting":
                if system.voting_enabled is True:
                    system.voting_enabled = False

                    voter = Voter.objects.all()

                    for c in range(len(candidates)):
                        xt = 1
                        yt = 1
                        for v in voter: 
                            if v.vote is None or v.vote == "":
                                v.reference = generate_voter_reference(candidates)
                                v.a_reference, v.b_reference = encrypt_voter_reference(system, v.reference)

                                vote = ""
                                vote_enc = ""
                                for i in range(len(candidates)):
                                    vote += "0"
                                    if vote[i] == v.reference[i] :
                                        vote_enc += "-1,"
                                    else :
                                        vote_enc += "1,"
                                
                                print("\n" + v.name + "'s vote: " + vote)
                                print("\n" + v.name + "'s encrypted vote: " + vote_enc + "\n\n")

                                v.vote = vote_enc
                                v.save()

                            A = Decimal(v.a_reference.split(",")[c])
                            B = Decimal(v.b_reference.split(",")[c])

                            vote = Decimal(v.vote.split(",")[c])
                            xt *= pow(A, vote)
                            yt *= pow(B, vote)

                        candidates[c].xnt = str(xt)
                        candidates[c].ynt = str(yt)
                        candidates[c].save()

                else:
                    system.voting_enabled = True
            elif sender_type == "tallying_authority_registration":
                if system.tallying_authority_registration_open is True:
                    system.tallying_authority_registration_open = False
                else:
                    system.tallying_authority_registration_open = True

            system.save()

    return render(request, 'admin_dashboard.html', context)

def view_voters(request):
    voters = Voter.objects.all()

    context = {

    }

    try:
        if request.session['admin_email'] is not None :
            admin =  Admin.objects.get(email=request.session['admin_email'])
            context = {
                "admin_name": admin.name.upper(),
                "parent_path": "administrator/",
                "voters": voters
            }
        else:
            admin_logout(request)
    except Exception as _:
        admin_logout(request)

    if request.method == 'POST':
        voter_id = request.POST.get('voter_id')
        name = request.POST.get('voter_name')
        email = request.POST.get('voter_email')
        identity_number = request.POST.get('voter_identity_number')
        delete_id = request.POST.get('delete_id')

        if voter_id is not None and voter_id != "":
            # Edit Voter
            try:
                voter = Voter.objects.get(pk=voter_id)
                voter.name = name
                voter.email = email
                voter.identity_number = identity_number
                voter.save()

            except Exception as _:
                messages.error(request, f"Voter not found.")
        elif delete_id is not None and delete_id != "":
            #Delete Voter
            Voter.objects.get(pk=delete_id).delete()
        elif email is not None and email != "" and identity_number is not None and identity_number != "":
            #Add Voter
            v = Voter(name=name, email=email, identity_number=identity_number)
            v.save()

    return render(request, 'view_voters.html', context)

def view_candidates(request):
    try:
        if request.session['admin_email'] is not None :
            admin =  Admin.objects.get(email=request.session['admin_email'])
    except KeyError:
        pass


    candidates = Candidate.objects.all()

    context = {
        "admin_name": admin.name.upper(),
        "parent_path": "administrator/",
        "candidates": candidates
    }

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        name = request.POST.get('name')
        image = request.POST.get('image')
        delete_id = request.POST.get('delete_id')

        if candidate_id is not None and candidate_id != "":
            # Edit Candidate
            try:
                c = Candidate.objects.get(pk=candidate_id)
                c.name = name
                c.image = image
                c.save()

            except Exception as _:
                messages.error(request, f"Candidate not found.")
        elif delete_id is not None and delete_id != "":
            #Delete Candidate
            Candidate.objects.get(pk=delete_id).delete()
        elif name is not None and name != "" and image is not None and image != "":
            #Add Candidate
            c1 = Candidate(name=name, image=image)
            c1.save()

    return render(request, 'view_candidates.html', context)

def view_tallying_authorities(request):
    try:
        if request.session['admin_email'] is not None :
            admin =  Admin.objects.get(email=request.session['admin_email'])
    except KeyError:
        pass


    tallying_authorities = TallyingAuthority.objects.all()

    context = {
        "admin_name": admin.name.upper(),
        "parent_path": "administrator/",
        "tallying_authorities": tallying_authorities
    }

    if request.method == 'POST':
        tallying_authority_id = request.POST.get('tallying_authority_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        identity_number = request.POST.get('identity_number')
        delete_id = request.POST.get('delete_id')

        if tallying_authority_id is not None and tallying_authority_id != "":
            # Edit Tallying Authority
            try:
                ta = TallyingAuthority.objects.get(pk=tallying_authority_id)
                ta.name = name
                ta.email = email
                ta.identity_number = identity_number
                ta.save()

            except Exception as _:
                messages.error(request, f"Tallying Authority not found.")
        elif delete_id is not None and delete_id != "":
            #Delete Tallying Authority
            TallyingAuthority.objects.get(pk=delete_id).delete()
        elif email is not None and email != "" and identity_number is not None and identity_number != "":
            #Add Tallying Authority
            t = TallyingAuthority(name=name, email=email, identity_number=identity_number)
            t.save()

    return render(request, 'view_tallying_authorities.html', context)


###############################################
## BULLETIN BOARD
###############################################

def view_bulletin_board(request):
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    winner = ""

    if len(Candidate.objects.filter(yes_count="")) == 0:
        try:
            winner = Candidate.objects.order_by('-yes_count')[0].name
            print(winner)
        except Exception as e:
                logger.error(e)
    context = {
        "candidates": candidates,
        "voter_count": len(voters),
        "winner": winner
    }

    return render(request, 'bulletin_board.html', context)

###############################################
## LOGOUT
###############################################

def voter_logout(request):
    request.session['admin_email'] = None
    return redirect("/")

def tallying_authority_logout(request):
    request.session['admin_email'] = None
    return redirect("/")

def admin_logout(request):
    request.session['admin_email'] = None
    return redirect("/")

###############################################
## HELPER FUNCTIONS
###############################################

def add_candidates():
    candidate1 = Candidate(name="Haider Mirza", image="")
    candidate1.save()

    candidate2 = Candidate(name="John Doe", image="")
    candidate2.save()

    candidate3 = Candidate(name="Mark Johnson", image="")
    candidate3.save()
    logger.error("Candidates Added")

def add_voters():
    voter1 = Voter(name="Haider Mirza", email="haider@mailinator.com", identity_number="1001")
    voter1.save()

    voter2 = Voter(name="John Doe", email="john@mailinator.com", identity_number="1002")
    voter2.save()

    voter3 = Voter(name="Mark Johnson", email="mark@mailinator.com", identity_number="1003")
    voter3.save()

    voter4 = Voter(name="Peter Parker", email="peter@mailinator.com", identity_number="1004")
    voter4.save()
    
    voter5 = Voter(name="Tony Starks", email="tony@mailinator.com", identity_number="1005")
    voter5.save()

    voter6 = Voter(name="Steve Rogers", email="steve@mailinator.com", identity_number="1006")
    voter6.save()

    voter7 = Voter(name="Bruce Wayne", email="bruce@mailinator.com", identity_number="1007")
    voter7.save()

    voter8 = Voter(name="Tom Cruise", email="tom@mailinator.com", identity_number="1008")
    voter8.save()

    voter9 = Voter(name="Jane Doe", email="jane@mailinator.com", identity_number="1009")
    voter9.save()

    voter10 = Voter(name="David Sparks", email="david@mailinator.com", identity_number="1010")
    voter10.save()
    logger.error("Voters Added")


def add_tallying_authorities():
    tallyingAuthority1 = TallyingAuthority(name="Scott James", email="scott@mailinator.com", identity_number="2001")
    tallyingAuthority1.save()

    tallyingAuthority2 = TallyingAuthority(name="Kate Shephard", email="kate@mailinator.com", identity_number="2002")
    tallyingAuthority2.save()

    tallyingAuthority3 = TallyingAuthority(name="Morgan Jones", email="morgan@mailinator.com", identity_number="2003")
    tallyingAuthority3.save()
    logger.error("Tallying Authorities Added")


def clear_votes():
    for v in Voter.objects.all():
        v.has_voted = False
        v.is_registered = False
        v.reference = ""
        v.a_reference = ""
        v.b_reference = ""
        v.private_key = ""
        v.public_key = ""
        v.vote = ""
        v.save()

    for c in Candidate.objects.all():
        c.xnt = ""
        c.ynt = ""
        c.yes_count = ""
        c.no_count = ""
        c.save()

    for t in TallyingAuthority.objects.all():
        t.x_value = ""
        t.y_value = ""
        t.result_submitted = False
        t.is_registered = False
        t.private_key = ""
        t.public_key = ""

        t.save()

    print("CLEARED")

def clear_all_databases():
    System.objects.all().delete()
    Candidate.objects.all().delete()
    Voter.objects.all().delete()
    TallyingAuthority.objects.all().delete()
    logger.error("Database Cleared")


def setup_election_parameters():
    q = helper.generate_big_prime(4)
    G = helper.primRoots(q)
    g = G[randint(0,len(G)-1)]

    system = System(q=q, g=g)
    system.save()

    logger.error("g: " + str(g))
    logger.error("q: " + str(q))

    logger.error("Election Parameters Generated")

def generate_voter_reference(cd):
    candidate_count = len(cd)
    print("Candidate count: " + str(candidate_count))
    r = ""
    for _ in range(candidate_count):
        r += str(randint(0,1))

    logger.error("r: " + str(r))

    return r

def encrypt_voter_reference(sys, r):
    A_value = ""
    B_value = ""

    pub_keys = 1
    for t in tallying_authorities:
        pub_keys *= int(t.public_key)

    logger.error("pub_keys: " + str(pub_keys))

    for i in r:
        y = randint(1, int(sys.q)-1)
        A = pow(int(sys.g), y)

        py = pow(pub_keys, y)
        if i == "0":
            B = int(sys.g) * py
        elif i == "1":
            B = py / int(sys.g)

        A_value += str(A) + ","
        B_value += str(B) + ","

    logger.error("A:" + str(A_value))
    logger.error("B:" + str(B_value))

    return A_value, B_value

def test_system():
    clear_all_databases()

    ## 1. SETUP
    logger.error("\n-----------------Setup Stage-----------------\n")

    setup_election_parameters()

    add_candidates()
    add_voters()
    add_tallying_authorities()

    sys = System.objects.all()[0]
    cds = Candidate.objects.all()
    tas = TallyingAuthority.objects.all()
    voters = Voter.objects.all()

    for t in tas:
        x = randint(1, int(sys.q)-1)
        t.private_key = x
        logger.error("x: " + str(x))
        t.public_key = pow(int(sys.g), x)
        t.save()

        logger.error("Tallying Authority Private Key: " + str(t.private_key))
        logger.error("Tallying Authority Public Key: " + str(t.public_key))

    ## 2. REGISTRATION
    logger.error("\n-----------------Registration Stage-----------------\n")

    for v in voters:
        r = generate_voter_reference(cds)
        A, B = encrypt_voter_reference(sys, r)
        v.reference = r
        v.a_reference = A
        v.b_reference = B
        v.save()

    ## 3. VOTING

    logger.error("\n-----------------Voting Stage-----------------\n")

    for v in voters:
        vc = randint(0, len(candidates)-1)
        vote = ""
        vote_enc = ""
        ref = v.reference
        logger.error(v.name + "'s voted YES for Candidate: " + str(vc+1))

        for i in range(len(candidates)):
            if i == vc :
                vote += "1"
            else :
                vote += "0"

            # if (vote[i] == "1" and ref[i] == "1") or (vote[i] == "-1" and ref[i] == "0") :
            if vote[i] == ref[i] :
                vote_enc += "-1,"
            else :
                vote_enc += "1,"

        logger.error(v.name + "'s vote: " + vote.replace("0","-1"))
        logger.error(v.name + "'s reference: " + ref.replace("0","-1"))
        logger.error(v.name + "'s encrypted vote: " + vote_enc.replace("0","-1") + "\n\n")

        v.vote = vote_enc
        v.has_voted = True
        v.save()

        # vote1 = Votes(voter=v, vote=vote_enc)
        # vote1.save()
            
            
    ## 4. TALLYING

    logger.error("\n-----------------Tallying Stage-----------------\n")

    votes = Voter.objects.all()

    xnt = []
    ynt = []
    xij = []

    for c in range(len(candidates)):
        xt = 1
        yt = 1
        for v in votes: ## To check with supervisors
            A = Decimal(v.a_reference.split(",")[c])
            B = Decimal(v.b_reference.split(",")[c])

            vote = Decimal(v.vote.split(",")[c])
            xt *= pow(A, vote)
            yt *= pow(B, vote)
        xnt.append(xt)
        ynt.append(yt)

    for t in tallying_authorities:
        xij1 = []
        for j in range(len(candidates)):
            x = pow(xnt[j], Decimal(t.private_key))
            # t.x_value = x
            # t.save()
            xij1.append(x)
        xij.append(xij1)

            # logger.error(t.name + "'s X: " + str(x))

    print(*xnt)
    print(*ynt)
    print(*xij)

    # print("ynt: " + str(Decimal(sys.g)))

    ## ADMIN PART

    for j in range(len(candidates)):
        eq = 1
        for t in range(len(tallying_authorities)):
            eq *= pow(xij[t][j],-1)
        eq *= ynt[j]
    
        print("g: " + str(Decimal(sys.g)))
        print("eq: " + str(eq))

        zj = math.log(eq)/math.log(Decimal(sys.g))
        yj = (zj + len(votes))/2
        nj = len(votes) - yj

        print("Candidate " + str(j+1) + "'s YES count: " + str(yj))
        print("Candidate " + str(j+1) + "'s NO count: " + str(nj) + "\n")




    ## TESTING PURPOSES ONLY

    # xnt = [0.00032,244140625,625]
    # ynt = [7.3075081866545145910184250549280887399251968, 10644899600020376799775134290618272120616491835776704002312625229616022071863880340712592209318392254870227112931888813452986454239896673253979927798826631549424622369707424761806203422164097672008235806855657259485659071884811055497266352176666259765625, 293873587705571876992184134305561419454666389193021880377187926569604314863681793212890625]
    # xij = [[3.4359738368,51698788284564229679463043254372678347863256931304931640625,37252902984619140625],[3.6028797018963968,183670992315982423120115083940975887159166493245638675235742454106002696789801120758056640625,5684341886080801486968994140625],[3.6893488147419103232,10947644252537633366591637369452469775627046420910279466852095967888992833483285949114360846579074859619140625,2220446049250313080847263336181640625]]

    # eqj = [0.001600000000000000000000000195162925774229967039972988285256860763183794915676116943359375, 1.024000000000000085336494702168050619975588044762926717528597624122865306084292908095787714906974616342734496691029067572369356679163558667857770211146391097785660638109732653722002616030023708186547093390572626958601176738739013671875, 625]

    # # eqj = np.array()

    # for j in range(3):
    #     # eq = 1
    #     # for t in range(3):
    #     #     eq *= pow(xij[t][j],-1)
    #     # eq *= ynt[j]
    
    #     # print("g: " + str(13))
    #     print(eqj[j])

    #     zj = Decimal(math.log(eqj[j])/math.log(5))
    #     print("Z: " + str(zj))

    #     yj = (zj + 10)/2
    #     nj = 10 - yj

    #     print("Candidate " + str(j) + "'s YES count: " + str(yj))
    #     print("Candidate " + str(j) + "'s NO count: " + str(nj) + "\n")



           
    # logger.error("XT: " + str(xt))
    # logger.error("YT: " + str(yt))



