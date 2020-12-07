# edgarapp/views.py

import itertools
from datetime import datetime
from django.contrib import messages

import requests
import textdistance
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
# For contact View
from django.http import HttpResponse, HttpResponseRedirect
# 404 error page
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from django.views.decorators.gzip import gzip_page
from django.views.generic import ListView, TemplateView
import requests, os, os.path,mysql
from mysql.connector import Error, errorcode
from .forms import ContactForm, UsersLoginForm, UsersRegisterForm
from .models import Company, Directors, Executives, Filing, Funds, Proxies,FilingsExhibits
from .utils import TOCAlternativeExtractor, Printer
from .readfiling import readFiling,toc_exctract
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.exceptions import ObjectDoesNotExist
#from .config import  password,user,host,database

def handler404(request, *args, **argv):
    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    response = render_to_response('404.html', {'extended_template': extended_template},
                                  context_instance=RequestContext(request))
    response.status_code = 404

    return response


def HomePageView(request):
    template_name = 'home.html'

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


def SearchResultsView(request):
    # model = Company, Filing, Funds, Directors, Proxies, Executives
    # template_name  = 'companyOverview.html'

    extended_template = 'base_company.html'
    if request.user.is_authenticated:
        extended_template = 'base_company_member.html'

    query = request.GET.get('q')

    if not request.user.is_authenticated:
        # print("done")
        if query != 'TSLA':
            messages.error(request, 'To search for other Tickers,')
            return render(
                request, 'home.html',
                {'extended_template': extended_template}
            )
    mycompany = Company.objects.get(ticker=query)

    filing = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate').latest('filingdate');

    return HttpResponseRedirect('/filing/?q=' + query + '&fid=' + str(filing.cik))

    # -------------no need to carry out the other searches as they are expensive-----------------------"
    # filings = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate')
    # proxies = Proxies.objects.filter(cik=mycompany.cik).order_by('-filingdate')
    # name = mycompany.name
    # name = name.upper()
    # name = name.replace('INTERNATIONAL', 'INTL')
    # name = name.replace(' /DE', '')
    # name = name.replace('/DE', '')
    # name = name.replace('INC.', 'INC')
    # name = name.replace(',', '')

    # matches = []
    # exectable = []

    # funds = Funds.objects.raw(
    #     'SELECT * FROM edgarapp_funds WHERE company = %s ORDER BY share_prn_amount+0 DESC LIMIT 100', [name])
    #
    # directors = Directors.objects.filter(
    #     company=mycompany.name).order_by('-director')
    #
    # allDirectors = Directors.objects.all()

    # executives = Executives.objects.filter(company=mycompany.name)
    # today = datetime.today()
    # currYear = today.year
    #
    # for year in executives:
    #     if year.filingdate.split('-')[0] == str(currYear):
    #         exectable.append(year)
    #
    # for person in directors:
    #     if person:
    #         personA = person.director.replace("Mr.", '')
    #         personA = person.director.replace("Dr.", '')
    #         personA = person.director.replace("Ms.", '')
    #         a = set([s for s in personA if s != "," and s != "." and s != " "])
    #         aLast = personA.split(' ')[-1]
    #         if (len(personA.split(' ')) == 1):
    #             aLast = personA.split('.')[-1]
    #     comps = []
    #     for check in allDirectors:
    #         if person:
    #             personB = check.director.replace("Mr.", '')
    #             personB = check.director.replace("Dr.", '')
    #             personB = check.director.replace("Ms.", '')
    #             bLast = personB.split(' ')[-1]
    #             if (len(personB.split(' ')) == 1):
    #                 bLast = personB.split('.')[-1]
    #             # print(personA, aLast, person.company, personB, bLast, check.company)
    #             if aLast == bLast:
    #                 # first check jaccard index to speed up algo, threshold of .65
    #                 b = set([s for s in personB if s !=
    #                          "," and s != "." and s != " "])
    #                 if (len(a.union(b)) != 0):
    #                     jaccard = float(
    #                         len(a.intersection(b)) / len(a.union(b)))
    #                 else:
    #                     jaccard = 1
    #                 # print(personA, personB, jaccard)
    #                 if (jaccard > 0.65):
    #                     # run Ratcliff-Obershel for further matching, threshold of .75 and prevent self-match
    #                     sequence = textdistance.ratcliff_obershelp(
    #                         personA, personB)
    #                     # print(sequence)
    #                     if sequence > 0.75 and mycompany.name != check.company:
    #                         comps.append(check.company)
    #     if not comps:
    #         comps.append('Director is not on the board of any other companies')
    #     matches.append(comps)
    #
    # object_list = []
    # object_list.append(query)
    # object_list.append((mycompany.name, mycompany.ticker))
    # object_list.append(filings)
    # object_list.append(funds)
    # object_list.append(zip(directors, matches))
    # object_list.append(zip(exectable, matches))
    # object_list.append(itertools.zip_longest(proxies, filings, fillvalue='foo'))

    # object_list is (q, (companyname, ticker), (filings object))
    # if request.user.is_authenticated:
    # print(object_list)

    latest_filing = []
    # for file in filings:

    # filing = Filing.objects.filter(cik=mycompany.cik).order_by('-filingdate').first()
    # print(filing)
    # url ='E:/Workspace/mblazr/edgarapp/static'+'/'+ 'filings/' + filing.filingpath
    # toc_extractor = TOCExtractor()
    # with open(url) as file:
    #
    #     filing_html = file.read()
    #
    #     try:
    #         extract_data = toc_extractor.extract(filing_html)
    #         table_of_contents = extract_data.table
    #     except:
    #        table_of_contents = ""
    # 'filing_html': filing_html,'table_of_contents': table_of_contents

    # return render(
    # request, template_name,
    # {'object_list': object_list, 'extended_template': extended_template,
    #  'table_of_contents': table_of_contents,
    #   'filing_html': filing_html
    #    }
    # )
    # else:
    #     if query == 'HD':
    #         return render(
    #             request, template_name,
    #             {'object_list': object_list, 'extended_template': extended_template}
    #         )
    #     else:
    #         return render(request, 'about.html', {'extended_template': 'base.html'})


@gzip_page
def SearchFilingView(request):
    template_name = 'companyFiling.html'
    extended_template = 'base_company.html'
    global filing_to_display,filings_list
    q_company = request.GET.get('q')
    q_filing = request.GET.get('fid')
    if q_company == '' or q_company == None:
        q_company='TSLA'

    if q_filing=='' or q_filing == None:
        q_filing='all'
    else:
        try:
            int(q_filing)
        except:
            q_filing='all'



    #Authentication here
    if not request.user.is_authenticated and q_company != 'TSLA':
        # redirect them to login
        return redirect('/accounts/login/?next=' + q_company)

    elif request.user.is_authenticated or (not request.user.is_authenticated and q_company == 'TSLA'):
        #Check query being searched
        company_search = Company.objects.filter(ticker=q_company)

        if len(company_search)>0:
            #Company is valid
            filings_for_company = Filing.objects.filter(cik=company_search[0].cik)

            if len(filings_for_company)>0:
                filings_list=[]

                #Prepare Filings List (to didplay on left side)
                for myfiling in filings_for_company:
                    filings_list.append(myfiling.dict_values())
                #We have filings for that Company
                if q_filing == 'all':
                    filing_to_display = filings_for_company[0]
                else:
                    result_for_fid = Filing.objects.filter(cik=company_search[0].cik,id=q_filing)
                    if len(result_for_fid)==1:
                      filing_to_display =result_for_fid[0]
                    else:
                      #Output First Filing automaticaly
                      filing_to_display = filings_for_company[0]


                #Now we have filings as well as complete company info
                company_cik = company_search[0].cik
                company_name = company_search[0].name
                company_ticker =company_search[0].ticker

                #Get directors,executives,funds
                funds = Funds.objects.filter(company=company_name)[:100]
                directors = Directors.objects.filter(company=company_name)
                executives = Executives.objects.filter(company=company_name)

                object_list=[]

                #Fetch file and prepare TOC
                #Check  the Filing Data
                all_parts = str(filing_to_display.filingpath).split('/')

                path_to_extract_toc =''
                path_of_filing =''

                if(len(all_parts)==4): #filings/files/val/file.ht
                    path_to_extract_toc = str(filing_to_display.filingpath).split('/')[2]+'/'+ str(filing_to_display.filingpath).split('/')[-1]
                    path_of_filing = path_to_extract_toc
                elif (len(all_parts)==2): #cikvalue/file.htm
                    path_to_extract_toc = str(filing_to_display.filingpath)
                    path_of_filing =path_to_extract_toc

                fetched_filing = readFiling(path_to_extract_toc)

                #print(fetched_filing)
                # #t_o_c = filing_to_display.table_of_contents.first()
                # #if not t_o_c :
                toc_extractor = TOCAlternativeExtractor()
                extract_data = toc_extractor.extract(fetched_filing)
                t_o_c = filing_to_display.table_of_contents.create(body=extract_data.table)

                filing_toc =t_o_c.body


                return render(
                    request, template_name, {
                        'object_list': object_list,
                        'company_filings': filings_list,
                        'company_ticker': company_ticker,
                        'directors': directors,
                        'executives': executives,
                        'company_name': company_name,
                        'current_filing': filing_to_display,
                        'funds': funds,
                        'extended_template': extended_template,
                        'table_of_contents': filing_toc,  # prep,  # t_o_c.body,#updatedtoc,
                        'fid': company_cik,
                        'filepath': path_of_filing

                    })
            else:

                    #No filing in Od Db as well
                    return HttpResponse(status=404,content='<h3 style="text-align:center">No filings for '+str(company_search[0].name)+ ' was found.Check back later',content_type='text/html')
        else:
            #Company could Not be found so redirect to home page

            return HttpResponseRedirect('/')


@gzip_page
def SearchFilingView2(request):
    template_name = 'companyFiling.html'

    extended_template = 'base_company.html'
    if request.user.is_authenticated:
        extended_template = 'base_company_member.html'

    matches = []
    exectable = []

    # Check to ensure query value is not empty if empty we search for tesla
    if request.GET.get('q') != None or request.GET.get('q') != '':
        query = request.GET.get('q')
    else:
        query = 'TSLA'

    # user is not logged in and
    # they are not searching for Tesla
    if not request.user.is_authenticated and query != 'TSLA':
        # redirect them to login
        return redirect('/accounts/login/?next=' + query)

    elif request.user.is_authenticated or (not request.user.is_authenticated and query == 'TSLA'):
        # user is authenticated or they are not authenticated but are searching for Tesla
        # check if query sqtring has valid arguments
        try:
            comp_searched = Company.objects.filter(ticker=str(query))
        except ObjectDoesNotExist:
            comp_searched = Company.objects.all()
        except Exception as e:
            print(e)
            comp_searched = Company.objects.all()

        fid = request.GET.get('fid')
        Filings_list = Filing.objects.all()
        if fid == 'all':
            # query string fetches the latest filing

            filing = Filing.objects.filter(cik=comp_searched[0].cik).first()

            # the latest filing is being recieved
        else:
            # normal fid is in place

            filing = Filing.objects.filter(cik=comp_searched[0].cik, id=fid)[0]  # the filing was requested by fid
            print("Filing was using id")

        company_filings = [filing.dict_values() for filing in Filings_list]
        # print(company_filings)

    links = []
    verify = []

    company = filing.name
    company_ticker = comp_searched[0].ticker
    print("company searched "+str(comp_searched[0].name))

    #   name = mycompany.name
    #   name = name.upper()
    #   name = name.replace('INTERNATIONAL', 'INTL')
    #   name = name.replace(' /DE', '')
    #   name = name.replace('/DE', '')
    #   name = name.replace('INC.', 'INC')
    #   name = name.replace(',', '')

    # funds = Funds.objects.raw(
    #   'SELECT * FROM edgarapp_funds WHERE company = %s ORDER BY share_prn_amount+0 DESC LIMIT 100', [name])
    funds = Funds.objects.filter(company=company)[:100]
    # 'SELECT * FROM edgarapp_funds WHERE company = %s ORDER BY share_prn_amount+0 DESC LIMIT 100', [name])

    # directors = Directors.objects.filter(company=mycompany.name).order_by('-director')
    directors = Directors.objects.filter(company=company)

    # allDirectors = Directors.objects.all()

    executives = Executives.objects.filter(company=company)
    # executives = company.executives.all()

    # today = datetime.today()
    # currYear = today.year

    # for year in executives:
    #     if year.filingdate.split('-')[0] == str(currYear):
    #         exectable.append(year)

    # for person in directors:
    #     if person:
    #         personA = person.director.replace("Mr.", '')
    #         personA = person.director.replace("Dr.", '')
    #         personA = person.director.replace("Ms.", '')
    #         a = set([s for s in personA if s != "," and s != "." and s != " "])
    #         aLast = personA.split(' ')[-1]
    #         if (len(personA.split(' ')) == 1):
    #             aLast = personA.split('.')[-1]
    # comps = []
    # for check in allDirectors:
    #     if person:
    #         personB = check.director.replace("Mr.", '')
    #         personB = check.director.replace("Dr.", '')
    #         personB = check.director.replace("Ms.", '')
    #         bLast = personB.split(' ')[-1]
    #         if (len(personB.split(' ')) == 1):
    #             bLast = personB.split('.')[-1]
    #         print(personA, aLast, person.company, personB, bLast, check.company)
    #         if aLast == bLast:
    #             # first check jaccard index to speed up algo, threshold of .65
    #             b = set([s for s in personB if s !=
    #                     "," and s != "." and s != " "])
    #             if (len(a.union(b)) != 0):
    #                 jaccard = float(
    #                     len(a.intersection(b)) / len(a.union(b)))
    #             else:
    #                 jaccard = 1
    #                 # print(personA, personB, jaccard)
    #             if (jaccard > 0.65):
    #                     # run Ratcliff-Obershel for further matching, threshold of .75 and prevent self-match
    #                 sequence = textdistance.ratcliff_obershelp(
    #                     personA, personB)
    #                 if sequence > 0.75 and mycompany.name != check.company:
    #                     comps.append(check.company)
    # if not comps:
    #     comps.append('Director is not on the board of any other companies')
    # matches.append(comps)

    object_list = []
    # object_list.append((query, fid))
    # object_list.append((mycompany.name, mycompany.ticker))
    # object_list.append(company_filings)
    # object_list.append(filing)
    # object_list.append(funds)
    # object_list.append(zip(directors, matches))
    # object_list.append(zip(exectable, matches))
    # object_list.append(links)

    company_name = company
    # company_ticker = company

    # url = '/mnt/filings-static/capitalrap/edgarapp/static/filings/' + filing.filingpath
    # print(filing.filingpath.split('files/')[1])
    #print("Now looking for toc")
    file_recieved = readFiling(filing.filingpath)  # readFiling(filing.filingpath.split('files/')[1])  for mblazr
    exctracted_toc = toc_exctract(file_recieved)
    #print("Done looking for toc")
    # t_o_c = filing.table_of_contents.first()
    # print(t_o_c)
    # t_o_c =None;
    # if not t_o_c :
    #
    #     toc_extractor = TOCAlternativeExtractor()
    #
    #     extract_data = toc_extractor.extract(file_recieved)
    #     t_o_c = filing.table_of_contents.create(body=extract_data.table)
    #     print('--resulf for toc ---')
    #     print(t_o_c.body)
    # updatedtoc =t_o_c.body

    # elif len(file_recieved) < 1:
    #     t_o_c = {'a': ''}
    #     t_o_c['body'] = ''
    #
    # try:
    #     updatedtoc=t_o_c.body
    # except:
    #     updatedtoc=''

    # -----------------new toc------#



    return render(
        request, template_name, {
            'object_list': object_list,
            'company_filings': company_filings,
            'company_ticker': company_ticker,
            'directors': directors,
            'executives': executives,
            'company_name': company_name,
            'current_filing': filing,
            'funds': funds,
            'extended_template': extended_template,
            'table_of_contents': exctracted_toc,#prep,  # t_o_c.body,#updatedtoc,
            'fid': filing.cik,
            'filepath': filing.filingpath

        }
    )

@xframe_options_exempt
def filing_fetch(request, id, file):

    try:
        data = readFiling(str(id) + '/' + str(file))

        if len(data) < 1:
            data = '<html></head><head><body><h4 style="text-align:center">Filing not available currently.Please check back later</h4></body></html>'

        return HttpResponse(status=200, content_type="text/html", content=data)
    except:
        return HttpResponse(status=500, content_type="text/html ",
                            content="<h3 style='text-align:center'>Something went wrong while we were getting the filings.Please chack back later</h3>")


def AboutView(request):
    template_name = 'about.html'
    extended_template = 'base.html'

    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


def HedgeFundView(request):
    template_name = 'hedgeFunds.html'
    extended_template = 'base.html'

    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


def FaqView(request):
    template_name = 'faq.html'
    extended_template = 'base.html'

    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    return render(
        request, template_name,
        {'extended_template': extended_template}
    )


# for contact


def contactView(request):
    form = ContactForm(request.POST or None)

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    if form.is_valid():
        name = form.cleaned_data.get("name")
        email = form.cleaned_data.get("email")
        message = form.cleaned_data.get("message")
        subject = "CapitalRap Contact Form: " + name

        comment = name + " with the email, " + email + \
                  ", sent the following message:\n\n" + message
        send_mail(subject, comment, settings.EMAIL_HOST_USER,
                  [settings.EMAIL_HOST_USER])

        context = {'form': form, 'extended_template': extended_template}
        messages.info(request, 'Thank you for contacting us!')
        return HttpResponseRedirect(request.path_info)

    else:
        context = {'form': form, 'extended_template': extended_template}
        return render(
            request, 'contact.html', context,
        )

    # if request.method == 'GET':
    #    form = ContactForm()
    # else:
    #    form = ContactForm(request.POST)
    #    if form.is_valid():
    #        name = form.cleaned_data['name']
    #        email = form.cleaned_data['email']
    #        message = form.cleaned_data['message']
    #        try:
    #            send_mail('CapitalRap Contact Form '+name+' '+email, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
    #        except BadHeaderError:
    #            return HttpResponse('Invalid header found.') #TODO: ADD MESSAGE INSTEAD
    #        messages.info(request, 'Thank you for contacting us!')
    #        return HttpResponseRedirect(request.path_info)
    # return render(request, "contact.html", {'form': form})


##################
## Members side ##


def login_view(request):
    form = UsersLoginForm(request.POST or None)

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'home.html'

    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)

        if request.GET.get('next') == None:
            return redirect('home')
        else:
            return redirect('/filing/?q=' + request.GET.get('next') + '&fid=all')
    return render(request, "form.html", {
        "form": form,
        "title": "Login",
        'extended_template': extended_template,
    })


def register_view(request):
    form = UsersRegisterForm(request.POST or None)

    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'

    if form.is_valid():
        user = form.save()
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        if request.GET.get('next') == None:
            return redirect('home')
        else:
            return redirect('/filing/?q=' + request.GET.get('next') + '&fid=all')

    return render(request, "form.html", {
        "title": "Register",
        "form": form,
        'extended_template': extended_template,
    })


@login_required
def account_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _(
                'Your password was successfully updated!'))
            return redirect('account')
        else:
            messages.error(request, _('There was an error. Try again!'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account.html', {
        'form': form
    })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")


def PlanView(request):
    extended_template = 'base.html'
    if request.user.is_authenticated:
        extended_template = 'base_member.html'
    return render(request, 'plan.html', {'extended_template': extended_template,
                                         })


def PrinterView(request, fid, start):
    try:
        filing = Filing.objects.get(id=fid)
    except:
        return HttpResponse(status=404, content="Requested Filing Could not be Found for printing")

    url = readFiling(filing.filingpath)
    if start == 'full':
        return HttpResponseRedirect('/getfiling/' + filing.filingpath)
    else:
        printer = Printer().generate(url, start)

        return render(request, 'printer.html', {'html': printer})
